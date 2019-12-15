#!/home/prilog/.pyenv/versions/3.6.9/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, Response, abort, session, redirect
from wtforms import Form, StringField, SubmitField, validators, ValidationError
import numpy as np
import os
import re
from pytube import YouTube
import sys
import time as tm
sys.path.append('/home/prilog/lib')
import cv2


characters_data = np.load("model/UB_name.npy")

sec_data = np.load("model/timer_sec.npy")

characters = [
    "アオイ",
    "アオイ(編入生)",
    "アカリ",
    "アキノ",
    "アヤネ",
    "アヤネ(クリスマス)",
    "アユミ",
    "アリサ",
    "アン",
    "アンナ",
    "イオ",
    "イオ(サマー)",
    "イリヤ",
    "エミリア",
    "エリコ",
    "エリコ(バレンタイン)",
    "カオリ",
    "カオリ(サマー)",
    "カスミ",
    "カヤ",
    "キャル",
    "キャル(☆6以降)",
    "キャル(サマー)",
    "キョウカ",
    "キョウカ(ハロウィン)",
    "クウカ",
    "クウカ(オーエド)",
    "クリスティーナ",
    "クリスティーナ(クリスマス)",
    "クルミ",
    "クルミ(クリスマス)",
    "グレア",
    "クロエ",
    "コッコロ",
    "コッコロ(☆6以降)",
    "コッコロ(サマー)",
    "サレン",
    "サレン(サマー)",
    "ジータ",
    "シオリ",
    "シズル",
    "シズル(バレンタイン)",
    "シノブ",
    "シノブ(ハロウィン)",
    "ジュン",
    "スズナ",
    "スズナ(サマー)",
    "スズメ",
    "スズメ(サマー)",
    "タマキ",
    "タマキ(サマー)",
    "チカ",
    "チカ(クリスマス)",
    "ツムギ",
    "トモ",
    "ナナカ",
    "ニノン",
    "ニノン(オーエド)",
    "ネネカ",
    "ノゾミ",
    "ノゾミ(クリスマス)",
    "ハツネ",
    "ヒヨリ",
    "ヒヨリ(ニューイヤー)",
    "ペコリーヌ",
    "ペコリーヌ(☆6以降)",
    "ペコリーヌ(サマー)",
    "マコト",
    "マコト(サマー)",
    "マツリ",
    "マヒル",
    "マホ",
    "マホ(サマー)",
    "ミサキ",
    "ミサキ(ハロウィン)",
    "ミサト",
    "ミソギ",
    "ミソギ(ハロウィン)",
    "ミツキ",
    "ミフユ",
    "ミフユ(サマー)",
    "ミミ",
    "ミミ(ハロウィン)",
    "ミヤコ",
    "ミヤコ(ハロウィン)",
    "ムイミ",
    "モニカ",
    "ユイ",
    "ユイ(ニューイヤー)",
    "ユカリ",
    "ユキ",
    "ヨリ",
    "ラム",
    "リノ",
    "リノ(☆6以降)",
    "リマ",
    "リマ(☆6以降)",
    "リン",
    "ルゥ",
    "ルカ",
    "ルナ",
    "レイ",
    "レイ(ニューイヤー)",
    "レム",
]

timer = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
]

FRAME_COLS = 1280
FRAME_ROWS = 720

UB_ROI = (440, 100, 860, 130)
MIN_ROI = (1072, 24, 1090, 42)
TENSEC_ROI = (1090, 24, 1108, 42)
ONESEC_ROI = (1104, 24, 1122, 42)

TIMER_MIN = 2
TIMER_TENSEC = 1
TIMER_SEC = 0

UB_THRESH = 0.6
TIMER_THRESH = 0.75

FOUND = 1
NOT_FOUND = 0

NO_ERROR = 0
ERROR_BAD_URL = 1
ERROR_TOO_LONG = 2
ERROR_NOT_SUPPORTED = 3
ERROR_CANT_GET_MOVIE = 4

streamDir = "tmp/"
if not os.path.exists(streamDir):
    os.mkdir(streamDir)


def search(youtube_id):
    # ID部分の取り出し
    work_id = re.findall('.*watch(.{14})', youtube_id)
    if not work_id:
        work_id = re.findall('.youtu.be/(.{11})', youtube_id)
        if not work_id:
            return None, None, None, None, ERROR_BAD_URL
        work_id[0] = '?v=' + work_id[0]
    # Youtubeから動画を保存し保存先パスを返す
    youtubeUrl = 'https://www.youtube.com/watch' + work_id[0]
    try:
        yt = YouTube(youtubeUrl)
    except:
        return None, None, None, None, ERROR_CANT_GET_MOVIE

    movieThumbnail = yt.thumbnail_url
    movieLength = yt.length
    if int(movieLength) > 480:
        return None, None, None, None, ERROR_TOO_LONG

    stream = yt.streams.get_by_itag("22")
    if stream is None:
        return None, None, None, None, ERROR_NOT_SUPPORTED

    movieTitle = stream.title
    movieName = tm.time()
    moviePath = stream.download(streamDir, str(movieName))
    return moviePath, movieTitle, movieLength, movieThumbnail, NO_ERROR


def analyze_movie(movie_path):
    # 動画解析し結果をリストで返す
    startTime = tm.time()
    video = cv2.VideoCapture(movie_path)

    frame_count = int(video.get(7))  # フレーム数を取得
    frame_rate = int(video.get(5))  # フレームレート(1フレームの時間単位はミリ秒)の取得

    frame_width = int(video.get(3))  # フレームの幅
    frame_height = int(video.get(4))  # フレームの高さ

    if frame_width != int(FRAME_COLS) or frame_height != int(FRAME_ROWS):
        return None

    n = 0.34  # n秒ごと*
    ubInterval = 0

    timeMin = "1"
    timeSec10 = "3"
    timeSec1 = "0"

    ubData = []
    timeData = []
    characters_find = []

    cap_interval = int(frame_rate * n)
    skip_frame = 5 * cap_interval

    if (frame_count / frame_rate) < 600:  # 10分未満の動画しか見ない
        for i in range(frame_count):  # 動画の秒数を取得し、回す
            ret = video.grab()
            if ret is False:
                break

            if i % cap_interval is 0:
                if ((i - ubInterval) > skip_frame) or (ubInterval == 0):
                    ret, work_frame = video.read()

                    if ret is False:
                        break
                    work_frame = edit_frame(work_frame)

                    if timeMin is "1":
                        timeMin = analyze_timer_frame(work_frame, MIN_ROI, 2, timeMin)

                    timeSec10 = analyze_timer_frame(work_frame, TENSEC_ROI, 6, timeSec10)
                    timeSec1 = analyze_timer_frame(work_frame, ONESEC_ROI, 10, timeSec1)

                    result = analyze_ub_frame(work_frame, timeMin, timeSec10, timeSec1, ubData, characters_find)

                    if result is FOUND:
                        ubInterval = i

    video.release()
    os.remove(movie_path)
    time_after = tm.time() - startTime
    timeData.append("動画時間 : {:.3f}".format(frame_count / frame_rate) + "  sec")
    timeData.append("処理時間 : {:.3f}".format(time_after) + "  sec")
    return ubData, timeData


def edit_frame(frame):
    work_frame = frame

#    work_frame = cv2.resize(work_frame, dsize=(FRAME_COLS, FRAME_ROWS))
    work_frame = cv2.cvtColor(work_frame, cv2.COLOR_RGB2GRAY)
    ret, work_frame = cv2.threshold(work_frame, 200, 255, cv2.THRESH_BINARY)
    work_frame = cv2.bitwise_not(work_frame)

    return work_frame


def analyze_ub_frame(frame, time_min, time_10sec, time_sec, ub_data, characters_find):
    analyze_frame = frame[UB_ROI[1]:UB_ROI[3], UB_ROI[0]:UB_ROI[2]]

    characters_num = len(characters)

    if len(characters_find) < 5:
        for j in range(characters_num):
            result_temp = cv2.matchTemplate(analyze_frame, characters_data[j], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
            if max_val > UB_THRESH:
                ub_data.append(time_min + ":" + time_10sec + time_sec + " " + characters[j])
                if j not in characters_find:
                    characters_find.append(j)
                return FOUND
    else:
        for j in range(5):
            result_temp = cv2.matchTemplate(analyze_frame, characters_data[characters_find[j]], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
            if max_val > UB_THRESH:
                ub_data.append(time_min + ":" + time_10sec + time_sec + " " + characters[characters_find[j]])
                return FOUND

    return NOT_FOUND


def analyze_timer_frame(frame, roi, data_num, time_data):
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    """
    cv2.namedWindow('window')
    cv2.imshow('window', analyze_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """

    for j in range(data_num):
        result_temp = cv2.matchTemplate(analyze_frame, sec_data[j], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
        if max_val > TIMER_THRESH:
            return timer[j]

    return time_data


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'zJe09C5c3tMf5FnNL09C5e6SAzZuY'


class UrlForm(Form):
    Url = StringField("Youtube Id",
                              [validators.InputRequired("この項目は入力必須です"),
                               validators.length(min=11, max=100,
                                                 message="URLはhttps://www.youtube.com/watch?v=...の形式でお願いします")])

    # html側で表示するsubmitボタンの表示
    submit = SubmitField("解析")


@app.route('/', methods=['GET', 'POST'])
def predicts():
    form = UrlForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            return render_template('index.html', form=form)
        else:
            Url = (request.form["Url"])

            path, title, length, thumbnail, result = search(Url)
            if result is ERROR_BAD_URL:
                error = "URLはhttps://www.youtube.com/watch?v=...の形式でお願いします"
                return render_template('index.html', form=form, error=error)
            elif result is ERROR_TOO_LONG:
                error = "動画時間が長すぎるため、解析に対応しておりません"
                return render_template('index.html', form=form, error=error)
            elif result is ERROR_NOT_SUPPORTED:
                error = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"
                return render_template('index.html', form=form, error=error)
            elif result is ERROR_CANT_GET_MOVIE:
                error = "動画の取得に失敗しました。もう一度入力をお願いします"
                return render_template('index.html', form=form, error=error)
            session['path'] = path
            session['title'] = title
            length = int(int(length) / 4)
            return render_template('analyze.html', title=title, length=length, thumbnail=thumbnail)

    elif request.method == 'GET':
        path = session.get('path')
        session.pop('path', None)

        if path is not None:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    print("PermissionError occur")

        return render_template('index.html', form=form)


@app.route('/result', methods=['GET', 'POST'])
def analyze():
    path = session.get('path')
    title = session.get('title')
    session.pop('path', None)
    session.pop('title', None)

    if request.method == 'GET' and path is not None:
        timeline, timedata = analyze_movie(path)
        if timeline is not None:
            session.pop('checking', None)
            return render_template('result.html', title=title, timeLine=timeline, timeData=timedata)
        else:
            return redirect("/")
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run()
