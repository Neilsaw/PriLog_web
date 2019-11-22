#!/home/prilog/.pyenv/versions/3.6.9/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, Response, abort
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
    "キャル",
    "キャル(☆6以降)",
    "キャル(サマー)",
    "キョウカ",
    "キョウカ(ハロウィン)",
    "クウカ",
    "クウカ(オーエド)",
    "クリスティーナ",
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
TIMER_THRESH = 0.7

FOUND = 1
NOT_FOUND = 0

streamDir = "tmp/"
if not os.path.exists(streamDir):
    os.mkdir(streamDir)


def search(youtube_id):
    # ID部分の取り出し
    work_id = re.findall('.*watch(.{14})', youtube_id)
    if not work_id:
        return None, None
    # Youtubeから動画を保存し保存先パスを返す
    youtubeUrl = 'https://www.youtube.com/watch' + work_id[0]
    yt = YouTube(youtubeUrl)
    if int(yt.length) > 480:
        return None, None
    stream = yt.streams.get_by_itag("22")
    movieTitle = stream.title
    movieName = tm.time()
    moviePath = stream.download(streamDir, str(movieName))
    return moviePath, movieTitle


def analyze_movie(movie_path):
    # 動画解析し結果をリストで返す
    startTime = tm.time()
    video = cv2.VideoCapture(movie_path)

    frame_count = int(video.get(7))  # フレーム数を取得
    frame_rate = int(video.get(5))  # フレームレート(1フレームの時間単位はミリ秒)の取得

    n = 0.5  # n秒ごと*
    ubInterval = 0

    timeMin = "1"
    timeSec10 = "3"
    timeSec1 = "0"

    ubData = []
    characters_find = []

    cap_interval = int(frame_rate * n)
    skip_frame = 4 * cap_interval

    if (frame_count / frame_rate) < 600:  # 10分未満の動画しか見ない
        for i in range(frame_count):  # 動画の秒数を取得し、回す
            ret = video.grab()
            if ret is False:
                break

            if i % cap_interval is 0:
                ret, work_frame = video.read()
                if ret is False:
                    break
                work_frame = edit_frame(work_frame)

                if ((i - ubInterval) > skip_frame) or (ubInterval == 0):

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
    ubData.append("")
    ubData.append("\n動画時間 : {:.3f}".format(frame_count / frame_rate) + "  sec")
    ubData.append("処理時間 : {:.3f}".format(time_after) + "  sec")
    return ubData


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


class IrisForm(Form):
    SepalLength = StringField("Youtube Id",
                              [validators.InputRequired("この項目は入力必須です"),
                               validators.length(min=11, max=100, message="正しいURLを入力して下さい。")])

    # html側で表示するsubmitボタンの表示
    submit = SubmitField("解析")


@app.route('/', methods=['GET', 'POST'])
def predicts():
    form = IrisForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            flash("入力する必要があります。")
            return render_template('index.html', form=form)
        else:
            SepalLength = (request.form["SepalLength"])

            moviePath, movieTitle = search(SepalLength)
            if moviePath is None:
                flash("この動画の解析は対応してません。")
                return render_template('index.html', form=form)
            timeline = analyze_movie(moviePath)

            return render_template('result.html', irisName=movieTitle, timeLine=timeline)
    elif request.method == 'GET':

        return render_template('index.html', form=form)


if __name__ == "__main__":
    app.run()
