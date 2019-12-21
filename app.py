#!/home/prilog/.pyenv/versions/3.6.9/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, redirect
import numpy as np
import os
import re
from pytube import YouTube
import time as tm
import cv2

# キャラクター名テンプレート
characters_data = np.load("model/UB_name.npy")

# 時間テンプレート
sec_data = np.load("model/timer_sec.npy")

# キャラクター名一覧
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
    "イオ",      # ☆6以降
    "イオ(サマー)",
    "イリヤ",
    "イリヤ(クリスマス)",
    "エミリア",
    "エリコ",
    "エリコ(バレンタイン)",
    "カオリ",
    "カオリ(サマー)",
    "カスミ",
    "カヤ",
    "キャル",
    "キャル",      # ☆6以降
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
    "コッコロ",      # ☆6以降
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
    "ペコリーヌ",      # ☆6以降
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
    "リノ",      # ☆6以降
    "リマ",
    "リマ",      # ☆6以降
    "リン",
    "ルゥ",
    "ルカ",
    "ルナ",
    "レイ",
    "レイ(ニューイヤー)",
    "レム",
]

# 時間一覧
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
TEN_SEC_ROI = (1090, 24, 1108, 42)
ONE_SEC_ROI = (1104, 24, 1122, 42)

TIMER_MIN = 2
TIMER_TEN_SEC = 1
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

stream_dir = "tmp/"
if not os.path.exists(stream_dir):
    os.mkdir(stream_dir)


def search(youtube_id):
    # ID部分の取り出し
    work_id = re.findall('.*watch(.{14})', youtube_id)
    if not work_id:
        work_id = re.findall('.youtu.be/(.{11})', youtube_id)
        if not work_id:
            return None, None, None, None, ERROR_BAD_URL
        work_id[0] = '?v=' + work_id[0]
    # Youtubeから動画を保存し保存先パスを返す
    youtube_url = 'https://www.youtube.com/watch' + work_id[0]
    try:
        yt = YouTube(youtube_url)
    except:
        return None, None, None, None, ERROR_CANT_GET_MOVIE

    movie_thumbnail = yt.thumbnail_url
    movie_length = yt.length
    if int(movie_length) > 480:
        return None, None, None, None, ERROR_TOO_LONG

    stream = yt.streams.get_by_itag("22")
    if stream is None:
        return None, None, None, None, ERROR_NOT_SUPPORTED

    movie_title = stream.title
    movie_name = tm.time()
    movie_path = stream.download(stream_dir, str(movie_name))

    return movie_path, movie_title, movie_length, movie_thumbnail, NO_ERROR


def analyze_movie(movie_path):
    # 動画解析し結果をリストで返す
    start_time = tm.time()
    video = cv2.VideoCapture(movie_path)

    frame_count = int(video.get(7))  # フレーム数を取得
    frame_rate = int(video.get(5))  # フレームレート(1フレームの時間単位はミリ秒)の取得

    frame_width = int(video.get(3))  # フレームの幅
    frame_height = int(video.get(4))  # フレームの高さ

    if frame_width != int(FRAME_COLS) or frame_height != int(FRAME_ROWS):
        video.release()
        os.remove(movie_path)

        return None, None

    n = 0.34  # n秒ごと*
    ub_interval = 0

    time_min = "1"
    time_sec10 = "3"
    time_sec1 = "0"

    ub_data = []
    time_data = []
    characters_find = []

    cap_interval = int(frame_rate * n)
    skip_frame = 5 * cap_interval

    if (frame_count / frame_rate) < 600:  # 10分未満の動画しか見ない
        for i in range(frame_count):  # 動画の秒数を取得し、回す
            ret = video.grab()
            if ret is False:
                break

            if i % cap_interval is 0:
                if ((i - ub_interval) > skip_frame) or (ub_interval == 0):
                    ret, work_frame = video.read()

                    if ret is False:
                        break
                    work_frame = edit_frame(work_frame)

                    if time_min is "1":
                        time_min = analyze_timer_frame(work_frame, MIN_ROI, 2, time_min)

                    time_sec10 = analyze_timer_frame(work_frame, TEN_SEC_ROI, 6, time_sec10)
                    time_sec1 = analyze_timer_frame(work_frame, ONE_SEC_ROI, 10, time_sec1)

                    ub_result = analyze_ub_frame(work_frame, time_min, time_sec10, time_sec1, ub_data, characters_find)

                    if ub_result is FOUND:
                        ub_interval = i

    video.release()
    os.remove(movie_path)
    time_result = tm.time() - start_time
    time_data.append("動画時間 : {:.3f}".format(frame_count / frame_rate) + "  sec")
    time_data.append("処理時間 : {:.3f}".format(time_result) + "  sec")

    return ub_data, time_data


def edit_frame(frame):
    work_frame = frame

    work_frame = cv2.cvtColor(work_frame, cv2.COLOR_RGB2GRAY)
    work_frame = cv2.threshold(work_frame, 200, 255, cv2.THRESH_BINARY)[1]
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

    for j in range(data_num):
        result_temp = cv2.matchTemplate(analyze_frame, sec_data[j], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
        if max_val > TIMER_THRESH:
            return timer[j]

    return time_data


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'zJe09C5c3tMf5FnNL09C5e6SAzZuY'


@app.route('/', methods=['GET', 'POST'])
def predicts():
    if request.method == 'POST':
        Url = (request.form["Url"])

        path, title, length, thumbnail, url_result = search(Url)
        if url_result is ERROR_BAD_URL:
            error = "URLはhttps://www.youtube.com/watch?v=...の形式でお願いします"
            return render_template('index.html', error=error)
        elif url_result is ERROR_TOO_LONG:
            error = "動画時間が長すぎるため、解析に対応しておりません"
            return render_template('index.html', error=error)
        elif url_result is ERROR_NOT_SUPPORTED:
            error = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"
            return render_template('index.html', error=error)
        elif url_result is ERROR_CANT_GET_MOVIE:
            error = "動画の取得に失敗しました。もう一度入力をお願いします"
            return render_template('index.html', error=error)
        session['path'] = path
        session['title'] = title
        length = int(int(length) / 4) + 3

        return render_template('analyze.html', title=title, length=length, thumbnail=thumbnail)

    elif request.method == 'GET':
        path = session.get('path')
        session.pop('path', None)

        error = None
        if path is ERROR_NOT_SUPPORTED:
            error = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"

        elif path is not None:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    print("PermissionError occur")

        return render_template('index.html', error=error)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    path = session.get('path')
    session.pop('path', None)

    if request.method == 'GET' and path is not None:
        time_line, time_data = analyze_movie(path)
        if time_line is not None:
            session['time_line'] = time_line
            session['time_data'] = time_data
            session.pop('checking', None)
            return render_template('analyze.html')
        else:
            session['path'] = ERROR_NOT_SUPPORTED
            return render_template('analyze.html')
    else:
        return redirect("/")


@app.route('/result', methods=['GET', 'POST'])
def result():
    title = session.get('title')
    time_line = session.get('time_line')
    time_data = session.get('time_data')
    session.pop('title', None)
    session.pop('time_line', None)
    session.pop('time_data', None)

    if request.method == 'GET' and time_line is not None:
        return render_template('result.html', title=title, timeLine=time_line, timeData=time_data)
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run()
