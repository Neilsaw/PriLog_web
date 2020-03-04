# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, redirect, jsonify
import numpy as np
import os
import re
from pytube import YouTube
from pytube import extract
from pytube import exceptions
import time as tm
import cv2
import json
import urllib.parse
import characters as cd
import after_caluculation as ac

# キャラクター名テンプレート
characters_data = np.load("model/UB_name.npy")

# 時間テンプレート
sec_data = np.load("model/timer_sec.npy")

# MENUテンプレート
menu_data = np.load("model/menu.npy")

# スコアテンプレート
score_data = np.load("model/score_data.npy")

# ダメージ数値テンプレート
damage_data = np.load("model/damage_data.npy")

# アンナアイコンテンプレート
icon_data = np.load("model/icon_data.npy")

# キャラクター名一覧
characters = cd.characters_name

# 数値一覧
numbers = [
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

# 解析可能な解像度
FRAME_COLS = 1280
FRAME_ROWS = 720

# 画像認識範囲
UB_ROI = (490, 98, 810, 132)
MIN_ROI = (1068, 22, 1091, 44)
TEN_SEC_ROI = (1089, 22, 1109, 44)
ONE_SEC_ROI = (1103, 22, 1123, 44)
MENU_ROI = (1100, 0, 1280, 90)
SCORE_ROI = (160, 630, 290, 680)
DAMAGE_DATA_ROI = (35, 50, 255, 100)
CHARACTER_ICON_ROI = (234, 506, 1046, 668)

MENU_LOC = (63, 23)

# 時刻格納位置
TIMER_MIN = 2
TIMER_TEN_SEC = 1
TIMER_SEC = 0

# 認識判定値
UB_THRESH = 0.6
TIMER_THRESH = 0.7
MENU_THRESH = 0.6
DAMAGE_THRESH = 0.65
ICON_THRESH = 0.6

FOUND = 1
NOT_FOUND = 0

# エラーリスト
NO_ERROR = 0
ERROR_BAD_URL = 1
ERROR_TOO_LONG = 2
ERROR_NOT_SUPPORTED = 3
ERROR_CANT_GET_MOVIE = 4
ERROR_REQUIRED_PARAM = 5
ERROR_PROCESS_FAILED = 6

# キャッシュ格納数
CACHE_NUM = 5

stream_dir = "tmp/"
if not os.path.exists(stream_dir):
    os.mkdir(stream_dir)

cache_dir = "cache/"
if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)


pending_dir = "pending/"
if not os.path.exists(pending_dir):
    os.mkdir(pending_dir)


def cache_check(youtube_id):
    # キャッシュ有無の確認
    try:
        cache_path = cache_dir + urllib.parse.quote(youtube_id) + '.json'
        ret = json.load(open(cache_path))
        if len(ret) is CACHE_NUM:
            # キャッシュから取得した値の数が規定値
            return ret
        else:
            # 異常なキャッシュの場合
            clear_path(cache_path)
            return False

    except FileNotFoundError:
        return False


def pending_append(path):
    # 解析中のIDを保存
    try:
        with open(path, mode='w'):
            pass
    except FileExistsError:
        pass

    return


def clear_path(path):
    # ファイルの削除
    try:
        os.remove(path)
    except PermissionError:
        pass
    except FileNotFoundError:
        pass

    return


def get_youtube_id(url):
    # ID部分の取り出し
    try:
        ret = extract.video_id(url)
    except exceptions.RegexMatchError:
        ret = False

    return ret


def search(youtube_id):
    # youtubeの動画を検索し取得
    youtube_url = 'https://www.youtube.com/watch?v=' + youtube_id
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
        clear_path(movie_path)

        return None, None, None, None, ERROR_NOT_SUPPORTED

    n = 0.34  # n秒ごと*
    ub_interval = 0

    time_min = "1"
    time_sec10 = "3"
    time_sec1 = "0"

    menu_check = False

    min_roi = MIN_ROI
    tensec_roi = TEN_SEC_ROI
    onesec_roi = ONE_SEC_ROI
    ub_roi = UB_ROI
    score_roi = SCORE_ROI
    damage_data_roi = DAMAGE_DATA_ROI

    ub_data = []
    ub_data_value = []
    time_data = []
    characters_find = []

    tmp_damage = []
    total_damage = False

    cap_interval = int(frame_rate * n)
    skip_frame = 5 * cap_interval

    if (frame_count / frame_rate) < 600:  # 10分未満の動画しか見ない
        for i in range(frame_count):  # 動画の秒数を取得し、回す
            ret = video.grab()
            if ret is False:
                break

            if i % cap_interval is 0:
                if ((i - ub_interval) > skip_frame) or (ub_interval == 0):
                    ret, original_frame = video.read()

                    if ret is False:
                        break
                    work_frame = edit_frame(original_frame)

                    if menu_check is False:
                        menu_check, menu_loc = analyze_menu_frame(work_frame, menu_data, MENU_ROI)
                        if menu_check is True:
                            loc_diff = np.array(MENU_LOC) - np.array(menu_loc)
                            roi_diff = (loc_diff[0], loc_diff[1], loc_diff[0], loc_diff[1])
                            min_roi = np.array(MIN_ROI) - np.array(roi_diff)
                            tensec_roi = np.array(TEN_SEC_ROI) - np.array(roi_diff)
                            onesec_roi = np.array(ONE_SEC_ROI) - np.array(roi_diff)
                            ub_roi = np.array(UB_ROI) - np.array(roi_diff)
                            score_roi = np.array(SCORE_ROI) - np.array(roi_diff)
                            damage_data_roi = np.array(DAMAGE_DATA_ROI) - np.array(roi_diff)

                            analyze_anna_icon_frame(work_frame, CHARACTER_ICON_ROI, characters_find)

                    else:
                        if time_min is "1":
                            time_min = analyze_timer_frame(work_frame, min_roi, 2, time_min)

                        time_sec10 = analyze_timer_frame(work_frame, tensec_roi, 6, time_sec10)
                        time_sec1 = analyze_timer_frame(work_frame, onesec_roi, 10, time_sec1)

                        ub_result = analyze_ub_frame(work_frame, ub_roi, time_min, time_sec10, time_sec1,
                                                     ub_data, ub_data_value, characters_find)

                        if ub_result is FOUND:
                            ub_interval = i

                        # スコア表示の有無を確認
                        ret = analyze_score_frame(work_frame, score_data, score_roi)

                        if ret is True:
                            # 総ダメージ解析
                            ret = analyze_damage_frame(original_frame, damage_data_roi, tmp_damage)

                            if ret is True:
                                total_damage = "総ダメージ " + ''.join(tmp_damage)

                            break

    video.release()
    clear_path(movie_path)

    # TLに対する後処理
    debuff_value = ac.make_ub_value_list(ub_data_value, characters_find)

    time_result = tm.time() - start_time
    time_data.append("動画時間 : {:.3f}".format(frame_count / frame_rate) + "  sec")
    time_data.append("処理時間 : {:.3f}".format(time_result) + "  sec")

    return ub_data, time_data, total_damage, debuff_value, NO_ERROR


def edit_frame(frame):
    # フレームを二値化
    work_frame = frame

    work_frame = cv2.cvtColor(work_frame, cv2.COLOR_RGB2GRAY)
    work_frame = cv2.threshold(work_frame, 200, 255, cv2.THRESH_BINARY)[1]
    work_frame = cv2.bitwise_not(work_frame)

    return work_frame


def analyze_ub_frame(frame, roi, time_min, time_10sec, time_sec, ub_data, ub_data_value, characters_find):
    # ub文字位置を解析　5キャラ見つけている場合は探索対象を5キャラにする
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    characters_num = len(characters)
    ub_result = NOT_FOUND
    tmp_character = [False, 0]
    tmp_value = UB_THRESH

    if len(characters_find) < 5:
        # 全キャラ探索
        for j in range(characters_num):
            result_temp = cv2.matchTemplate(analyze_frame, characters_data[j], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
            if max_val > tmp_value:
                # 前回取得したキャラクターより一致率が高い場合
                tmp_character = [characters[j], j]
                tmp_value = max_val
                ub_result = FOUND

        if ub_result is FOUND:
            ub_data.append(time_min + ":" + time_10sec + time_sec + " " + tmp_character[0])
            ub_data_value.extend([[int(int(time_min) * 60 + int(time_10sec) * 10 + int(time_sec)), tmp_character[1]]])
            if tmp_character[1] not in characters_find:
                characters_find.append(tmp_character[1])
    else:
        for j in range(5):
            # 5キャラのみの探索
            result_temp = cv2.matchTemplate(analyze_frame, characters_data[characters_find[j]], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
            if max_val > tmp_value:
                # 前回取得したキャラクターより一致率が高い場合
                tmp_character = [characters[characters_find[j]], characters_find[j]]
                tmp_value = max_val
                ub_result = FOUND

        if ub_result is FOUND:
            ub_data.append(time_min + ":" + time_10sec + time_sec + " " + tmp_character[0])
            ub_data_value.extend([[int(int(time_min) * 60 + int(time_10sec) * 10 + int(time_sec)), tmp_character[1]]])

    return ub_result


def analyze_timer_frame(frame, roi, data_num, time_data):
    # 時刻位置の探索
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    tmp_number = time_data
    tmp_value = TIMER_THRESH

    for j in range(data_num):
        result_temp = cv2.matchTemplate(analyze_frame, sec_data[j], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
        if max_val > tmp_value:
            tmp_number = numbers[j]
            tmp_value = max_val

    return tmp_number


def analyze_menu_frame(frame, menu, roi):
    # menuの有無を確認し開始判定に用いる
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    result_temp = cv2.matchTemplate(analyze_frame, menu, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
    if max_val > MENU_THRESH:
        return True, max_loc

    return False, None


def analyze_score_frame(frame, score, roi):
    # scoreの有無を確認し終了判定に用いる
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    result_temp = cv2.matchTemplate(analyze_frame, score[0], cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
    if max_val > MENU_THRESH:
        return True

    return False


def analyze_damage_frame(frame, roi, damage):
    # 総ダメージを判定
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    analyze_frame = cv2.cvtColor(analyze_frame, cv2.COLOR_BGR2HSV)
    analyze_frame = cv2.inRange(analyze_frame, np.array([10, 120, 160]), np.array([40, 255, 255]))

    # 数値の存在位置特定
    find_list = find_damage_loc(analyze_frame)

    # 探索結果を座標の昇順で並べ替え
    find_list.sort()

    # 総ダメージ情報作成
    ret = make_damage_list(find_list, damage)

    return ret


def find_damage_loc(frame):
    # 数値の存在位置特定
    find_list = []
    number_num = len(numbers)

    for i in range(number_num):
        # テンプレートマッチングで座標取得
        result_temp = cv2.matchTemplate(frame, damage_data[i], cv2.TM_CCOEFF_NORMED)
        loc = np.where(result_temp > DAMAGE_THRESH)[1]
        result_temp = result_temp.T

        # 重複を削除し昇順に並び替える
        loc = list(set(loc))
        sort_loc = sorted(np.sort(loc))

        loc_number = len(sort_loc)

        # 座標に応じて数値を格納する
        if loc_number == 0:
            # 未発見の場合
            find_list.append([0, i, 0])
        elif loc_number == 1:
            # 座標一つの場合
            find_list.append([sort_loc[0], i, max(result_temp[sort_loc[0]])])
        else:
            # 座標複数の場合
            temp_loc = sort_loc[0]
            temp_value = max(result_temp[sort_loc[0]])

            # +5の範囲の値を同一視する
            for j in range(loc_number - 1):

                if sort_loc[j + 1] > sort_loc[j] + 5:
                    # 異なる座標の場合
                    find_list.append([temp_loc, i, temp_value])
                    temp_loc = sort_loc[j + 1]
                    temp_value = max(result_temp[sort_loc[j + 1]])

                else:
                    # +5の範囲の座標の場合
                    value_after = max(result_temp[sort_loc[j + 1]])

                    if value_after > temp_value:
                        # 直近探査結果より精度が上ならば更新する
                        temp_loc = sort_loc[j + 1]
                        temp_value = value_after

            find_list.append([temp_loc, i, temp_value])

    return find_list


def make_damage_list(find_list, damage):
    # 総ダメージ情報作成
    ret = False
    temp_list = []

    list_num = len(find_list)

    # 探索結果の中で同一座標の被りを除外する
    for i in range(list_num):
        if find_list[i][0] != 0:
            if not temp_list:
                temp_list = find_list[i]
                ret = True

            if find_list[i][0] > temp_list[0] + 5:
                # 異なる座標の場合
                damage.append(str(temp_list[1]))
                temp_list = find_list[i]

            else:
                # +5の範囲の座標の場合
                if find_list[i][2] > temp_list[2]:
                    # 直近探査結果より精度が上ならば更新する
                    temp_list = find_list[i]

    damage.append(str(temp_list[1]))

    return ret


def analyze_anna_icon_frame(frame, roi, characters_find):
    # アンナの有無を確認　UBを使わない場合があるため
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    icon_num = len(icon_data)

    for j in range(icon_num):
        result_temp = cv2.matchTemplate(analyze_frame, icon_data[j], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
        if max_val > ICON_THRESH:
            characters_find.append(characters.index('アンナ'))

    return


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'zJe09C5c3tMf5FnNL09C5e6SAzZuY'
app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['GET', 'POST'])
def predicts():
    if request.method == 'POST':
        url = (request.form["Url"])

        # urlからid部分の抽出
        youtube_id = get_youtube_id(url)
        if youtube_id is False:
            error = "URLはhttps://www.youtube.com/watch?v=...の形式でお願いします"
            return render_template('index.html', error=error)

        cache = cache_check(youtube_id)
        if cache is not False:
            title, time_line, time_data, total_damage, debuff_value = cache
            if time_line:
                debuff_dict = None
                if debuff_value:
                    debuff_dict = ({key: val for key, val in zip(time_line, debuff_value)})
                data_url = "https://prilog.jp/?v=" + youtube_id
                data_txt = "@PriLog_Rより%0a"
                data_txt += title + "%0a"
                if total_damage:
                    data_txt += total_damage + "%0a"

                return render_template('result.html', title=title, timeLine=time_line,
                                       timeData=time_data, totalDamage=total_damage, debuffDict=debuff_dict,
                                       data_txt=data_txt, data_url=data_url)
            else:
                error = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"
                return render_template('index.html', error=error)

        path, title, length, thumbnail, url_result = search(youtube_id)

        if url_result is ERROR_TOO_LONG:
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
        session['youtube_id'] = youtube_id
        length = int(int(length) / 8) + 3

        return render_template('analyze.html', title=title, length=length, thumbnail=thumbnail)

    elif request.method == 'GET':
        if 'v' in request.args:  # ?v=YoutubeID 形式のGETであればリザルト返却
            youtube_id = request.args.get('v')
            if re.fullmatch(r'^([a-zA-Z0-9_-]{11})$', youtube_id):
                cache = cache_check(youtube_id)
                if cache is not False:
                    title, time_line, time_data, total_damage, debuff_value = cache
                    if time_line:
                        debuff_dict = None
                        if debuff_value:
                            debuff_dict = ({key: val for key, val in zip(time_line, debuff_value)})
                        data_url = "https://prilog.jp/?v=" + youtube_id
                        data_txt = "@PriLog_Rより%0a"
                        data_txt += title + "%0a"
                        if total_damage:
                            data_txt += total_damage + "%0a"

                        return render_template('result.html', title=title, timeLine=time_line,
                                               timeData=time_data, totalDamage=total_damage, debuffDict=debuff_dict,
                                               data_txt=data_txt, data_url=data_url)
                    else:
                        error = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"
                        return render_template('index.html', error=error)
                else:  # キャッシュが存在しない場合は解析
                    path, title, length, thumbnail, url_result = search(youtube_id)

                    if url_result is ERROR_TOO_LONG:
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
                    session['youtube_id'] = youtube_id
                    length = int(int(length) / 8) + 3

                    return render_template('analyze.html', title=title, length=length, thumbnail=thumbnail)
            else:  # prilog.jp/(YoutubeID)に該当しないリクエスト
                error = "不正なリクエストです"
                return render_template('index.html', error=error)
        else:
            path = session.get('path')
            session.pop('path', None)
            session.pop('title', None)
            session.pop('youtube_id', None)

            error = None
            if path is ERROR_NOT_SUPPORTED:
                error = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"

            elif path is not None:
                clear_path(path)

            return render_template('index.html', error=error)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    path = session.get('path')
    title = session.get('title')
    youtube_id = session.get('youtube_id')
    session.pop('path', None)

    if request.method == 'GET' and path is not None:
        # TL解析
        time_line, time_data, total_damage, debuff_value, status = analyze_movie(path)

        # キャッシュ保存
        cache = cache_check(youtube_id)
        if cache is False:
            json.dump([title, time_line, False, total_damage, debuff_value],
                      open(cache_dir + urllib.parse.quote(youtube_id) + '.json', 'w'))

        if status is NO_ERROR:
            # 解析が正常終了ならば結果を格納
            session['time_line'] = time_line
            session['time_data'] = time_data
            session['total_damage'] = total_damage
            session['debuff_value'] = debuff_value
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
    total_damage = session.get('total_damage')
    debuff_value = session.get('debuff_value')
    youtube_id = session.get('youtube_id')
    session.pop('title', None)
    session.pop('time_line', None)
    session.pop('time_data', None)
    session.pop('total_damage', None)
    session.pop('debuff_value', None)
    session.pop('youtube_id', None)

    if request.method == 'GET' and time_line is not None:
        debuff_dict = None
        if debuff_value:
            debuff_dict = ({key: val for key, val in zip(time_line, debuff_value)})
        data_url = "https://prilog.jp/?v=" + youtube_id
        data_txt = "@PriLog_Rより%0a"
        data_txt += title + "%0a"
        if total_damage:
            data_txt += total_damage + "%0a"

        return render_template('result.html', title=title, timeLine=time_line,
                               timeData=time_data, totalDamage=total_damage, debuffDict=debuff_dict,
                               data_txt=data_txt, data_url=data_url)
    else:
        return redirect("/")


@app.route('/rest/analyze', methods=['POST', 'GET'])
def remoteAnalyze():
    status = NO_ERROR
    msg = "OK"
    result = {}

    ret = {}
    ret["result"] = result
    url = ""
    if request.method == 'POST':
        if "Url" not in request.form:
            status = ERROR_REQUIRED_PARAM
            msg = "必須パラメータがありません"

            ret["msg"] = msg
            ret["status"] = status
            return jsonify(ret)
        else:
            url = request.form['Url']

    elif request.method == 'GET':
        if "Url" not in request.args:
            status = ERROR_REQUIRED_PARAM
            msg = "必須パラメータがありません"

            ret["msg"] = msg
            ret["status"] = status
            return jsonify(ret)
        else:
            url = request.args.get('Url')

    # キャッシュ確認
    youtube_id = get_youtube_id(url)
    if youtube_id is False:
        # 不正なurlの場合
        status = ERROR_BAD_URL
        msg = "URLはhttps://www.youtube.com/watch?v=...の形式でお願いします"
    else:
        # 正常なurlの場合
        cache = cache_check(youtube_id)

        if cache is not False:
            # キャッシュ有りの場合

            # キャッシュを返信
            title, time_line, time_data, total_damage, debuff_value = cache
            if time_line:
                result["title"] = title
                result["total_damage"] = total_damage
                result["timeline"] = time_line
                result["process_time"] = time_data
                result["debuff_value"] = debuff_value
                result["timeline_txt"] = "\r\n".join(time_line)
                if debuff_value:
                    result["timeline_txt_debuff"] = "\r\n".join(list(
                        map(lambda x: "↓{} {}".format(str(debuff_value[x[0]][0:]).rjust(3, " "), x[1]),
                            enumerate(time_line))))
            else:
                status = ERROR_NOT_SUPPORTED
                msg = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"
        else:  # キャッシュ無しの場合
            # 解析中かどうかを確認
            pending_path = pending_dir + str(youtube_id)
            pending = os.path.exists(pending_path)
            if pending:  # 既に解析中の場合
                while True:  # 既に解析中の場合解析終了を監視
                    pending = os.path.exists(pending_path)
                    if pending:
                        tm.sleep(1)
                        continue
                    else:  # 既に開始されている解析が完了したら、そのキャッシュJSONを返す
                        cache = cache_check(youtube_id)
                        if cache is not False:
                            title, time_line, time_data, total_damage, debuff_value = cache
                            if time_line:
                                result["title"] = title
                                result["total_damage"] = total_damage
                                result["timeline"] = time_line
                                result["process_time"] = time_data
                                result["debuff_value"] = debuff_value
                                result["timeline_txt"] = "\r\n".join(time_line)
                                if debuff_value:
                                    result["timeline_txt_debuff"] = "\r\n".join(list(
                                        map(lambda x: "↓{} {}".format(str(debuff_value[x[0]][0:]).rjust(3, " "), x[1]),
                                            enumerate(time_line))))
                            break
                        else:  # キャッシュ未生成の場合
                            # キャッシュを書き出してから解析キューから削除されるため、本来起こり得ないはずのエラー
                            status = ERROR_PROCESS_FAILED
                            msg = "解析結果の取得に失敗しました"
                            break

            else:  # 既に解析中ではない場合
                # 解析キューに登録
                pending_append(pending_path)

                # youtube動画検索/検証
                path, title, length, thumbnail, url_result = search(youtube_id)
                status = url_result
                if url_result is ERROR_TOO_LONG:
                    msg = "動画時間が長すぎるため、解析に対応しておりません"
                elif url_result is ERROR_NOT_SUPPORTED:
                    msg = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"
                elif url_result is ERROR_CANT_GET_MOVIE:
                    msg = "動画の取得に失敗しました。もう一度入力をお願いします"
                else:
                    # TL解析
                    time_line, time_data, total_damage, debuff_value, analyze_result = analyze_movie(path)
                    status = analyze_result
                    # キャッシュ保存
                    cache = cache_check(youtube_id)
                    if cache is False:
                        json.dump([title, time_line, False, total_damage, debuff_value],
                                  open(cache_dir + urllib.parse.quote(youtube_id) + '.json', 'w'))

                    if analyze_result is NO_ERROR:
                        # 解析が正常終了ならば結果を格納
                        result["title"] = title
                        result["total_damage"] = total_damage
                        result["timeline"] = time_line
                        result["process_time"] = time_data
                        result["debuff_value"] = debuff_value

                        if time_line:
                            result["timeline_txt"] = "\r\n".join(time_line)
                            if debuff_value:
                                result["timeline_txt_debuff"] = "\r\n".join(list(
                                    map(lambda x: "↓{} {}".format(str(debuff_value[x[0]][0:]).rjust(3, " "), x[1]),
                                        enumerate(time_line))))

                    else:
                        msg = "非対応の動画です。「720p 1280x720」の一部の動画に対応しております"

                clear_path(pending_path)

    ret["msg"] = msg
    ret["status"] = status
    return jsonify(ret)


if __name__ == "__main__":
    app.run()
