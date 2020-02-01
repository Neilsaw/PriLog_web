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
import os, tkinter, tkinter.filedialog, tkinter.messagebox
import sys
import characters as cd


characters_data = np.load("model/UB_name.npy")

sec_data = np.load("model/timer_sec.npy")

menu_data = np.load("model/menu.npy")

damage_menu_data = np.load("model/damage_menu.npy")

characters = cd.characters_name

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
MENU_ROI = (1100, 0, 1280, 90)
DAMAGE_MENU_ROI = (1040, 38, 1229, 64)

MENU_LOC = (63, 23)

TIMER_MIN = 2
TIMER_TEN_SEC = 1
TIMER_SEC = 0

UB_THRESH = 0.6
TIMER_THRESH = 0.75
MENU_THRESH = 0.5

FOUND = 1
NOT_FOUND = 0


def edit_frame(frame):
    work_frame_a = frame

#    work_frame = cv2.resize(work_frame, dsize=(FRAME_COLS, FRAME_ROWS))
    work_frame_a = cv2.cvtColor(work_frame_a, cv2.COLOR_RGB2GRAY)
    ret_a, work_frame_a = cv2.threshold(work_frame_a, 200, 255, cv2.THRESH_BINARY)
    work_frame_a = cv2.bitwise_not(work_frame_a)

    return work_frame_a


def analyze_ub_frame(frame, roi, time_min, time_10sec, time_sec, characters_find):
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    characters_num = len(characters)

    if len(characters_find) < 5:
        for j in range(characters_num):
            result_temp = cv2.matchTemplate(analyze_frame, characters_data[j], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
            if max_val > UB_THRESH:
                print(time_min + ":" + time_10sec + time_sec + "	" + characters[j])
                if j not in characters_find:
                    characters_find.append(j)
                return FOUND

    else:
        for j in range(5):
            result_temp = cv2.matchTemplate(analyze_frame, characters_data[characters_find[j]], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
            if max_val > UB_THRESH:
                print(time_min + ":" + time_10sec + time_sec + "	" + characters[characters_find[j]])
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


def analyze_menu_frame(frame, menu, roi):
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    result_temp = cv2.matchTemplate(analyze_frame, menu, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
    if max_val > MENU_THRESH:
        return True, max_loc

    return False, None


root = tkinter.Tk()
root.withdraw()

fTyp = [("", "*")]

iDir = os.path.abspath(os.path.dirname(__file__))
file = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)

if file == "":
    print("No video source found")
    sys.exit(1)

movie_path = file

startTime = tm.time()
video = cv2.VideoCapture(movie_path)

frame_count = int(video.get(7))  # フレーム数を取得
frame_rate = int(video.get(5))  # フレームレート(1フレームの時間単位はミリ秒)の取得

frame_width = int(video.get(3))  # フレームの幅
frame_height = int(video.get(4))  # フレームの高さ

n = 0.5  # n秒ごと*
ubInterval = 0

time_min = "1"
time_sec10 = "3"
time_sec1 = "0"

ubData = []
characters_find = []

cap_interval = int(frame_rate * n)
skip_frame = 4 * cap_interval

menu_check = False

min_roi = MIN_ROI
tensec_roi = TEN_SEC_ROI
onesec_roi = ONE_SEC_ROI
ub_roi = UB_ROI
damage_menu_roi = DAMAGE_MENU_ROI

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

            if menu_check is False:
                menu_check, menu_loc = analyze_menu_frame(work_frame, menu_data, MENU_ROI)
                if menu_check is True:
                    loc_diff = np.array(MENU_LOC) - np.array(menu_loc)
                    roi_diff = (loc_diff[0], loc_diff[1], loc_diff[0], loc_diff[1])
                    min_roi = np.array(MIN_ROI) - np.array(roi_diff)
                    tensec_roi = np.array(TEN_SEC_ROI) - np.array(roi_diff)
                    onesec_roi = np.array(ONE_SEC_ROI) - np.array(roi_diff)
                    ub_roi = np.array(UB_ROI) - np.array(roi_diff)
                    damage_menu_roi = np.array(DAMAGE_MENU_ROI) - np.array(roi_diff)

            else:
                if ((i - ubInterval) > skip_frame) or (ubInterval == 0):

                    time_min = analyze_timer_frame(work_frame, min_roi, 2, time_min)

                    time_sec10 = analyze_timer_frame(work_frame, tensec_roi, 6, time_sec10)
                    time_sec1 = analyze_timer_frame(work_frame, onesec_roi, 10, time_sec1)

                    result = analyze_ub_frame(work_frame, ub_roi, time_min, time_sec10, time_sec1, characters_find)

                    if result is FOUND:
                        ubInterval = i

                    if time_min is "0" and time_sec10 is "0":
                        ret = analyze_menu_frame(work_frame, damage_menu_data, damage_menu_roi)[0]

                        if ret is True:
                            break

video.release()
time_after = tm.time() - startTime
print("\n動画時間 : {:.3f}".format(frame_count / frame_rate) + "  sec")
print("処理時間 : {:.3f}".format(time_after) + "  sec")
