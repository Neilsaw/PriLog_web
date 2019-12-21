# -*- coding: utf-8 -*-
import os
from pytube import YouTube
import cv2
import re
import sys
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


stream_dir = "movie/"
if not os.path.exists(stream_dir):
    os.mkdir(stream_dir)


def main():

    url_result, movie_path = get_youtube_movie()
    check_youtube_movie(url_result)
    analyze_movie(movie_path)


def get_youtube_movie():
    """get youtube movie from user input

    check user input url and check movie error

    Args:

    Returns:
        int: url error type
        str: movie path form user input url

    """

    print("Enter YouTube URL")
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
        print("URLはhttps://www.youtube.com/watch?v=...の形式でお願いします")
        sys.exit()
    elif url_result is ERROR_TOO_LONG:
        print("動画時間が長すぎるため、解析に対応しておりません")
        sys.exit()
    elif url_result is ERROR_NOT_SUPPORTED:
        print("非対応の動画です。「720p 1280x720」の一部の動画に対応しております")
        sys.exit()
    elif url_result is ERROR_CANT_GET_MOVIE:
        print("動画の取得に失敗しました。もう一度入力をお願いします")
        sys.exit()

    return


def analyze_movie(movie_path):
    """analyze movie for user select ub Mat

    Args:
        movie_path (str): movie path form user input url

    Returns:
        int: analyze result
        Mat: user select image

    """

    video = cv2.VideoCapture(movie_path)
    frame_que = deque([], 10)

    frame_count = int(video.get(7))  # フレーム数を取得
    frame_rate = int(video.get(5))  # フレームレート(1フレームの時間単位はミリ秒)の取得

    frame_width = int(video.get(3))  # フレームの幅
    frame_height = int(video.get(4))  # フレームの高さ

    if frame_width != int(FRAME_COLS) or frame_height != int(FRAME_ROWS):
        return None

    while True:
        print("Enter Analyze Start second")
        input_sec = input(">> ")
        skip_frame = int(int(input_sec) * frame_rate)

        if skip_frame > frame_count:
            over_time = (skip_frame - frame_count) / frame_rate
            print("your input time is longer than movie length, please input time. "
                  "over : " + str(over_time) + " seconds)")
        else:
            break

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

    video.release()
    os.remove(movie_path)
    return None


def edit_frame(frame):
    """edit movie frame to ub name ROI

    Args:
        frame (str): capture frame

    Returns:
        Mat: edited image as ub name

    """

    work_frame = frame

    work_frame = work_frame[UB_ROI[1]:UB_ROI[3], UB_ROI[0]:UB_ROI[2]]
    work_frame = cv2.cvtColor(work_frame, cv2.COLOR_RGB2GRAY)
    work_frame = cv2.threshold(work_frame, 200, 255, cv2.THRESH_BINARY)[1]
    work_frame = cv2.bitwise_not(work_frame)

    return work_frame


if __name__ == "__main__":
    main()




