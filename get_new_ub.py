# -*- coding: utf-8 -*-
import os
from pytube import YouTube
import cv2
import re
import sys
import shutil
import time as tm
from collections import deque


NO_ERROR = 0
ERROR_BAD_URL = 1
ERROR_TOO_LONG = 2
ERROR_NOT_SUPPORTED = 3
ERROR_CANT_GET_MOVIE = 4

FRAME_COLS = 1280
FRAME_ROWS = 720

UB_ROI = (520, 100, 780, 130)

BACKSPACE_KEY = 8
ENTER_KEY = 13
ESC_KEY = 27


stream_dir = "movie/"
if not os.path.exists(stream_dir):
    os.mkdir(stream_dir)


def main():

    url_result, movie_path = get_youtube_movie()
    check_youtube_movie(url_result)
    analyze_result, master_frame = analyze_movie(movie_path)

    if analyze_result is not True:
        print("対象フレームが見つかりませんでした。終了します")
        return -1

    character_name = get_character_name()

    save_learning_data(character_name, master_frame)

    print("画像の保存が完了しました。終了します")

    return 0


def get_youtube_movie():
    """get youtube movie from user input

    check user input url and check movie error

    Args:

    Returns:
        int: url error type
        str: movie path form user input url

    """

    print("\nYouTube URL を入力して下さい")
    input_url = input(">> ")

    work_id = re.findall(".*watch(.{14})", input_url)
    if not work_id:
        work_id = re.findall(".youtu.be/(.{11})", input_url)
        if not work_id:
            return ERROR_BAD_URL, None
        work_id[0] = "?v=" + work_id[0]

    youtube_url = "https://www.youtube.com/watch" + work_id[0]
    try:
        yt = YouTube(youtube_url)
    except:
        return ERROR_CANT_GET_MOVIE, None

    movie_length = yt.length
    if int(movie_length) > 480:
        return ERROR_TOO_LONG, None

    stream = yt.streams.get_by_itag("22")
    if stream is None:
        return ERROR_NOT_SUPPORTED, None

    movie_name = tm.time()
    movie_path = stream.download(stream_dir, str(movie_name))
    return NO_ERROR, movie_path


def check_youtube_movie(url_result):
    """check youtube movie from user input

    if movie has error, exit program

    Args:
        url_result (str): movie error type

    Returns:

    """

    if url_result is ERROR_BAD_URL:
        print("\nURLはhttps://www.youtube.com/watch?v=...の形式でお願いします")
        sys.exit()
    elif url_result is ERROR_TOO_LONG:
        print("\n動画時間が長すぎるため、解析に対応しておりません")
        sys.exit()
    elif url_result is ERROR_NOT_SUPPORTED:
        print("\n非対応の動画です。「720p 1280x720」の一部の動画に対応しております")
        sys.exit()
    elif url_result is ERROR_CANT_GET_MOVIE:
        print("\n動画の取得に失敗しました。もう一度入力をお願いします")
        sys.exit()

    return


def analyze_movie(movie_path):
    """analyze movie for user select ub Mat

    Args:
        movie_path (str): movie path form user input url

    Returns:
        Bool: analyze result
        Mat: user select image

    """

    video = cv2.VideoCapture(movie_path)
    frame_que = deque([], 10)

    frame_count = int(video.get(7))  # フレーム数を取得
    frame_rate = int(video.get(5))  # フレームレート(1フレームの時間単位はミリ秒)の取得

    frame_width = int(video.get(3))  # フレームの幅
    frame_height = int(video.get(4))  # フレームの高さ

    if frame_width != int(FRAME_COLS) or frame_height != int(FRAME_ROWS):
        video.release()
        os.remove(movie_path)
        return False, None

    while True:
        print("\n解析開始時刻(秒)を入力して下さい")
        input_sec = input(">> ")
        skip_frame = int(int(input_sec) * frame_rate)

        if skip_frame > frame_count:
            over_time = (skip_frame - frame_count) / frame_rate
            print("動画時間を超えています  超過 : " + str(over_time) + " 秒)")
        else:
            break
    print("\n操作方法")
    print("BackSpace : 前のフレーム / Enter : 次のフレーム / Esc : 確定\n")
    for i in range(frame_count):  # 動画の秒数を取得し、回す
        ret = video.grab()
        if ret is False:
            break

        if i > skip_frame:
            ret, work_frame = video.read()

            if ret is False:
                break

            work_frame = edit_frame(work_frame)
            frame_que.appendleft(work_frame)
            check_result, master_frame = image_check(frame_que)

            if check_result is True:
                video.release()
                os.remove(movie_path)
                return True, master_frame

    video.release()
    os.remove(movie_path)
    return False, None


def edit_frame(frame):
    """edit movie frame to ub name ROI

    Args:
        frame (str): capture frame

    Returns:
        Mat: edited image as ub name

    """

    work_frame = frame

    work_frame = work_frame[UB_ROI[1]:UB_ROI[3], UB_ROI[0]:UB_ROI[2]]

    return work_frame


def image_check(frame_que):
    """check movie for found ub master frame

    check frame que from [0] to last (Max 10 frame)

    user able to search frame with keyboard
    BackSpace: show previous frame
    Enter: show following frame, if this key push with latest frame, then read next frame
    Esc: select master frame

    Args:
        frame_que (deque): ub name que

    Returns:
        BOOL: image found (True) or not found (False)
        Mat: master_frame

    """

    frame_num = len(frame_que)
    frame_max = frame_num - 1
    que_index = 0

    while True:
        cv2.namedWindow('window')
        cv2.imshow('window', frame_que[que_index])
        key = cv2.waitKey(0) & 0xFF
        if key == BACKSPACE_KEY:
            if que_index < frame_max:
                # check continue to previous frame
                que_index += 1
                cv2.destroyAllWindows()

        elif key == ESC_KEY:
            # check finish confirm
            print("この画像で確定しますか？")
            print("BackSpace : 戻る / Enter : 確定\n")
            while True:
                confirm_key = cv2.waitKey(0) & 0xFF
                if confirm_key == BACKSPACE_KEY:
                    # check continue
                    cv2.destroyAllWindows()
                    break
                elif confirm_key == ENTER_KEY:
                    # check finish with find master frame
                    print("画像を確定しました\n")
                    return True, frame_que[que_index]

        elif key == ENTER_KEY:
            if que_index <= 0:
                # check finish with all frame has checked
                cv2.destroyAllWindows()
                break
            else:
                # check continue to following frame
                que_index -= 1
                cv2.destroyAllWindows()

    return False, None


def get_character_name():
    """get character name

    Args:

    Returns:
        str: character_name

    """

    while True:
        print("キャラクター名を入力して下さい")
        character_name = input(">> ")

        print("\n"+character_name + "　　でよろしいでしょうか？")
        print("BackSpace : 戻る / Enter : 確定\n")
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key == BACKSPACE_KEY:
                break
            elif key == ENTER_KEY:
                cv2.destroyAllWindows()
                print("名前を確定しました\n")
                return character_name


def save_learning_data(character_name, master_frame):
    """save learning data as image

    Args:
        character_name (str): image name
        master_frame (mat): master_frame

    Returns:

    """

    learning_dir = "learning_data/"
    if not os.path.exists(learning_dir):
        os.mkdir(learning_dir)

    image_dir = learning_dir + character_name + "/"
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)

    tmp_dir = learning_dir + "tmp/"
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    tmp_image_dir = tmp_dir + "1" + ".png"
    cv2.imwrite(tmp_image_dir, master_frame)

    shutil.move(tmp_image_dir, image_dir)

    return


if __name__ == "__main__":
    main()




