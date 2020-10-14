# -*- coding: utf-8 -*-
"""backend movie, get movie file

     * backend movie file to search timeline
     * get movie from YouTube as mp4 720p or 360p



"""
import numpy as np
from pytube import YouTube
from pytube import extract
from pytube import exceptions
import time as tm
import cv2
import characters as cd
import after_caluculation as ac
import app as ap
import common as cm
import state_list as state

# character name template
CHARACTERS_DATA = []

# timer template
SEC_DATA = []

# menu button template
MENU_DATA = []

# score template
SCORE_DATA = []

# total damage template
DAMAGE_DATA = []

# anna icon template
ICON_DATA = []

# SPEED icon template
SPEED_DATA = []

# character names
CHARACTERS = cd.characters_name

# numbers
NUMBERS = [
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

# analyzable resolution
FRAME_RESOLUTION = [
    # width, height
    (1280, 720),  # RESOLUTION_16_9
    (1280, 590),  # RESOLUTION_2_1_a
    (1280, 592),  # RESOLUTION_2_1_b
    (960, 720),  # RESOLUTION_4_3
    (640, 360)  # RESOLUTION_16_9_SD
]

RESOLUTION_16_9 = 0
RESOLUTION_2_1_a = 1
RESOLUTION_2_1_b = 2
RESOLUTION_4_3 = 3
RESOLUTION_16_9_SD = 4

# frame roi (x-min, y-min, x-max, y-max)
UB_ROI = (0, 0, 0, 0)
MIN_ROI = (0, 0, 0, 0)
TEN_SEC_ROI = (0, 0, 0, 0)
ONE_SEC_ROI = (0, 0, 0, 0)
MENU_ROI = (0, 0, 0, 0)
SCORE_ROI = (0, 0, 0, 0)
DAMAGE_DATA_ROI = (0, 0, 0, 0)
CHARACTER_ICON_ROI = (0, 0, 0, 0)
SPEED_ICON_ROI = (0, 0, 0, 0)
MENU_LOC = (0, 0)

FRAME_THRESH = 200
SPEED_ICON_THRESH = 240

# timer storage place
TIMER_MIN = 2
TIMER_TEN_SEC = 1
TIMER_SEC = 0

# analyze thresh values
UB_THRESH = 0.6
TIMER_THRESH = 0.6
MENU_THRESH = 0.6
DAMAGE_THRESH = 0.65
ICON_THRESH = 0.6
SPEED_THRESH = 0.4

FOUND = 1
NOT_FOUND = 0

# analyzable movie length (res:1s)
MOVIE_LENGTH_MAX = 600

ENEMY_UB = "――――敵UB――――"


def model_init(video_type):
    """init model

    init model for template matching

    Args:
        video_type (int): movie resolution type

    Returns:


    """
    global CHARACTERS_DATA  # character name template
    global SEC_DATA  # timer template
    global MENU_DATA  # menu button template
    global SCORE_DATA  # score template
    global DAMAGE_DATA  # total damage template
    global ICON_DATA  # anna icon template
    global SPEED_DATA  # SPEED icon template

    if video_type is RESOLUTION_16_9:
        CHARACTERS_DATA = np.load("model/16_9/UB_name_16_9.npy")
        SEC_DATA = np.load("model/16_9/timer_sec_16_9.npy")
        MENU_DATA = np.load("model/16_9/menu_16_9.npy")
        SCORE_DATA = np.load("model/16_9/score_data_16_9.npy")
        DAMAGE_DATA = np.load("model/16_9/damage_data_16_9.npy")
        ICON_DATA = np.load("model/16_9/icon_data_16_9.npy")
        SPEED_DATA = np.load("model/16_9/speed_data_16_9.npy")

    elif video_type is RESOLUTION_2_1_a:
        CHARACTERS_DATA = np.load("model/2_1/UB_name_2_1.npy")
        SEC_DATA = np.load("model/2_1/timer_sec_2_1.npy")
        MENU_DATA = np.load("model/2_1/menu_2_1.npy")
        SCORE_DATA = np.load("model/2_1/score_data_2_1.npy")
        DAMAGE_DATA = np.load("model/2_1/damage_data_2_1.npy")
        ICON_DATA = np.load("model/2_1/icon_data_2_1.npy")
        SPEED_DATA = np.load("model/2_1/speed_data_2_1.npy")

    elif video_type is RESOLUTION_2_1_b:
        CHARACTERS_DATA = np.load("model/2_1/UB_name_2_1.npy")
        SEC_DATA = np.load("model/2_1/timer_sec_2_1.npy")
        MENU_DATA = np.load("model/2_1/menu_2_1.npy")
        SCORE_DATA = np.load("model/2_1/score_data_2_1.npy")
        DAMAGE_DATA = np.load("model/2_1/damage_data_2_1.npy")
        ICON_DATA = np.load("model/2_1/icon_data_2_1.npy")
        SPEED_DATA = np.load("model/2_1/speed_data_2_1.npy")

    elif video_type is RESOLUTION_4_3:
        CHARACTERS_DATA = np.load("model/4_3/UB_name_4_3.npy")
        SEC_DATA = np.load("model/4_3/timer_sec_4_3.npy")
        MENU_DATA = np.load("model/4_3/menu_4_3.npy")
        SCORE_DATA = np.load("model/4_3/score_data_4_3.npy")
        DAMAGE_DATA = np.load("model/4_3/damage_data_4_3.npy")
        ICON_DATA = np.load("model/4_3/icon_data_4_3.npy")
        SPEED_DATA = np.load("model/4_3/speed_data_4_3.npy")

    elif video_type is RESOLUTION_16_9_SD:
        CHARACTERS_DATA = np.load("model/16_9/UB_name_16_9.npy")
        SEC_DATA = np.load("model/16_9/timer_sec_16_9.npy")
        MENU_DATA = np.load("model/16_9/menu_16_9.npy")
        SCORE_DATA = np.load("model/16_9/score_data_16_9.npy")
        DAMAGE_DATA = np.load("model/16_9/damage_data_16_9.npy")
        ICON_DATA = np.load("model/16_9/icon_data_16_9.npy")
        SPEED_DATA = np.load("model/16_9/speed_data_16_9.npy")

    return


def roi_init(video_type):
    """init roi and thresh value

    init roi for analyze and set thresh value

    Args:
        video_type (int): movie resolution type

    Returns:


    """
    global UB_ROI  # ub name analyze roi
    global MIN_ROI  # timer min analyze roi
    global TEN_SEC_ROI  # timer 10 sec analyze roi
    global ONE_SEC_ROI  # timer 1 sec analyze roi
    global MENU_ROI  # menu button analyze roi
    global SCORE_ROI  # score analyze roi
    global DAMAGE_DATA_ROI  # damage analyze roi
    global CHARACTER_ICON_ROI  # character icon analyze roi
    global SPEED_ICON_ROI  # speed icon analyze roi
    global MENU_LOC  # basic menu button location
    global UB_THRESH  # ub analyze thresh value
    global FRAME_THRESH  # frame color thresh value
    global SPEED_ICON_THRESH  # frame color thresh value

    if video_type is RESOLUTION_16_9:
        UB_ROI = (490, 98, 810, 132)
        MIN_ROI = (1068, 22, 1091, 44)
        TEN_SEC_ROI = (1089, 22, 1109, 44)
        ONE_SEC_ROI = (1103, 22, 1123, 44)
        MENU_ROI = (1100, 0, 1280, 90)
        SCORE_ROI = (160, 630, 290, 680)
        DAMAGE_DATA_ROI = (35, 40, 255, 100)
        CHARACTER_ICON_ROI = (234, 506, 1046, 668)
        SPEED_ICON_ROI = (1180, 616, 1271, 707)
        MENU_LOC = (63, 23)
        UB_THRESH = 0.6
        FRAME_THRESH = 200
        SPEED_ICON_THRESH = 240

    elif video_type is RESOLUTION_2_1_a:
        UB_ROI = (490, 76, 790, 102)
        MIN_ROI = (1040, 15, 1063, 33)
        TEN_SEC_ROI = (1058, 15, 1073, 33)
        ONE_SEC_ROI = (1069, 15, 1084, 33)
        MENU_ROI = (1050, 0, 1200, 50)
        SCORE_ROI = (265, 498, 365, 532)
        DAMAGE_DATA_ROI = (170, 23, 340, 80)
        CHARACTER_ICON_ROI = (300, 390, 970, 520)
        SPEED_ICON_ROI = (1122, 474, 1195, 542)
        MENU_LOC = (68, 17)
        UB_THRESH = 0.6
        FRAME_THRESH = 180
        SPEED_ICON_THRESH = 240

    elif video_type is RESOLUTION_2_1_b:
        UB_ROI = (490, 76, 790, 102)
        MIN_ROI = (1046, 15, 1069, 33)
        TEN_SEC_ROI = (1064, 15, 1079, 33)
        ONE_SEC_ROI = (1075, 15, 1090, 33)
        MENU_ROI = (1050, 0, 1200, 50)
        SCORE_ROI = (265, 498, 365, 532)
        DAMAGE_DATA_ROI = (170, 23, 340, 80)
        CHARACTER_ICON_ROI = (300, 390, 970, 520)
        SPEED_ICON_ROI = (1122, 474, 1195, 542)
        MENU_LOC = (75, 17)
        UB_THRESH = 0.6
        FRAME_THRESH = 180
        SPEED_ICON_THRESH = 240

    elif video_type is RESOLUTION_4_3:
        UB_ROI = (230, 70, 730, 102)
        MIN_ROI = (802, 14, 819, 34)
        TEN_SEC_ROI = (816, 14, 831, 34)
        ONE_SEC_ROI = (826, 14, 841, 34)
        MENU_ROI = (830, 0, 960, 50)
        SCORE_ROI = (120, 567, 210, 690)
        DAMAGE_DATA_ROI = (18, 115, 187, 175)
        CHARACTER_ICON_ROI = (170, 560, 790, 670)
        SPEED_ICON_ROI = (878, 639, 948, 709)
        MENU_LOC = (44, 17)
        UB_THRESH = 0.6
        FRAME_THRESH = 180
        SPEED_ICON_THRESH = 230

    elif video_type is RESOLUTION_16_9_SD:
        UB_ROI = (490, 98, 810, 132)
        MIN_ROI = (1068, 22, 1091, 44)
        TEN_SEC_ROI = (1089, 22, 1109, 44)
        ONE_SEC_ROI = (1103, 22, 1123, 44)
        MENU_ROI = (1100, 0, 1280, 90)
        SCORE_ROI = (160, 630, 290, 680)
        DAMAGE_DATA_ROI = (35, 40, 255, 100)
        CHARACTER_ICON_ROI = (234, 506, 1046, 668)
        SPEED_ICON_ROI = (1180, 616, 1271, 707)
        MENU_LOC = (63, 23)
        UB_THRESH = 0.4
        FRAME_THRESH = 160
        SPEED_ICON_THRESH = 240

    return


def get_youtube_id(url):
    """get youtube id from url

    if youtube id exist, pick up youtube id from url

    Args:
        url (string): user input url

    Returns:
        ret (string): youtube id from url

    """
    try:
        ret = extract.video_id(url)
    except exceptions.RegexMatchError:
        ret = False

    return ret


def search(youtube_id):
    """get movie from youtube

    get movie from YouTube iTag 22 (720p / mp4) or iTag 18 (360p / mp4)

    Args:
        youtube_id (str): user input youtube_id

    Returns:
        movie_path (str): movie save path
        movie_title (str): movie title
        movie_length (str): movie length
        movie_thumbnail (str): movie thumbnail url
        status (str): error status while get movie


    """
    # add dl ongoing queue
    dl_ongoing_path = ap.dl_ongoing_dir + str(youtube_id)
    cm.queue_append(dl_ongoing_path)

    youtube_url = "https://www.youtube.com/watch?v=" + youtube_id

    try:
        # add dl pending queue
        dl_pending_path = ap.dl_pending_dir + "pending"
        cm.queue_append(dl_pending_path)
        yt = YouTube(youtube_url)

    except KeyError as e:
        # cant get movie by status
        ret = state.ERR_PERM_UNEXPECTED
        error = e.args[0]
        if error == "cipher":
            ret = state.ERR_COPYRIGHTED_CONTENT
        elif error == "adaptiveFormats":
            ret = state.TMP_CANT_GET_HD
        elif error == "formats":
            ret = state.ERR_UNAVAILABLE_CONTENT

        cm.clear_path(dl_ongoing_path)
        return None, None, None, None, ret

    except exceptions.RegexMatchError:
        # cant get movie by private or deleted
        cm.clear_path(dl_ongoing_path)
        return None, None, None, None, state.TMP_CANT_GET_HD

    except:
        # cant get movie by other reason
        cm.clear_path(dl_ongoing_path)
        return None, None, None, None, state.TMP_CANT_GET_HD

    movie_thumbnail = yt.thumbnail_url
    movie_length = yt.length
    if int(movie_length) > MOVIE_LENGTH_MAX:
        cm.clear_path(dl_ongoing_path)
        return None, None, None, None, state.ERR_BAD_LENGTH

    status = state.DONE
    stream = yt.streams.get_by_itag(22)
    if stream is None:
        status = state.TMP_DONE_IN_SD
        stream = yt.streams.get_by_itag(18)
        if stream is None:
            cm.clear_path(dl_ongoing_path)
            return None, None, None, None, state.ERR_BAD_RESOLUTION

    movie_title = stream.title
    movie_name = tm.time()
    movie_path = stream.download(ap.stream_dir, str(movie_name))

    cm.clear_path(dl_ongoing_path)

    return movie_path, movie_title, movie_length, movie_thumbnail, status


def analyze_movie(movie_path):
    """analyze movie main

    check movie frames and find ub frame
    check frame: 0.34 sec (20 frames)

    Args
        movie_path (string): movie save path

    Returns
        ub_data (list): found ub data
        ub_data_enemy (list): found ub data with enemy ub
        time_data (list): spend time while analyze
        total_damage (string): total damage
        debuff_value (list): ub timing debuff values
        status (int): analyze status 200 (HD analyze) or 301 (SD analyze)


    """
    start_time = tm.time()
    video = cv2.VideoCapture(movie_path)

    frame_count = int(video.get(7))  # get total frame
    frame_rate = int(video.get(5))  # get frame rate

    frame_width = int(video.get(3))  # get frame width
    frame_height = int(video.get(4))  # get frame height

    try:
        video_type = FRAME_RESOLUTION.index((frame_width, frame_height))
    except ValueError:
        video.release()
        cm.clear_path(movie_path)

        return None, None, None, None, None, state.ERR_BAD_RESOLUTION

    model_init(video_type)
    roi_init(video_type)

    n = 0.34

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
    speed_roi = SPEED_ICON_ROI

    ub_data = []
    ub_data_enemy = []
    ub_data_value = []
    time_data = []
    characters_find = []

    tmp_damage = []
    total_damage = False

    cap_interval = int(frame_rate * n)
    past_time = 90
    time_count = 0
    find_id = -1
    find_count = 0

    if (frame_count / frame_rate) < 600:  # only check less than 10 min movie
        for i in range(frame_count):  # cycle check movie per frame
            ret = video.grab()
            if ret is False:
                break

            if i % cap_interval is 0:
                ret, original_frame = video.read()

                if ret is False:
                    break

                if video_type is RESOLUTION_16_9_SD:
                    original_frame = expand_frame(original_frame)

                work_frame = edit_frame(original_frame)

                if menu_check is False:
                    menu_check, menu_loc = analyze_menu_frame(work_frame, MENU_DATA, MENU_ROI)
                    if menu_check is True:
                        loc_diff = np.array(MENU_LOC) - np.array(menu_loc)
                        roi_diff = (loc_diff[0], loc_diff[1], loc_diff[0], loc_diff[1])
                        min_roi = np.array(MIN_ROI) - np.array(roi_diff)
                        tensec_roi = np.array(TEN_SEC_ROI) - np.array(roi_diff)
                        onesec_roi = np.array(ONE_SEC_ROI) - np.array(roi_diff)
                        ub_roi = np.array(UB_ROI) - np.array(roi_diff)
                        score_roi = np.array(SCORE_ROI) - np.array(roi_diff)
                        damage_data_roi = np.array(DAMAGE_DATA_ROI) - np.array(roi_diff)
                        speed_roi = np.array(SPEED_ICON_ROI) - np.array(roi_diff)

                        analyze_anna_icon_frame(work_frame, CHARACTER_ICON_ROI, characters_find)

                else:
                    if time_min is "1":
                        time_min = analyze_timer_frame(work_frame, min_roi, 2, time_min)

                    time_sec10 = analyze_timer_frame(work_frame, tensec_roi, 6, time_sec10)
                    time_sec1 = analyze_timer_frame(work_frame, onesec_roi, 10, time_sec1)

                    find_time = time_min + ":" + time_sec10 + time_sec1
                    now_time, is_same_time = time_check(time_min, time_sec10, time_sec1, past_time)

                    is_normal_speed = analyze_speed(original_frame, speed_roi)

                    if is_same_time:
                        #  count up if normal speed, neither, reset count
                        if is_normal_speed:
                            time_count += 1
                        else:
                            time_count = 0
                    else:
                        time_count = 0
                        past_time = now_time

                    if time_count >= 0:
                        # check friendly ub
                        ub_result, find_id, find_count = analyze_ub_frame(work_frame, ub_roi, time_min, time_sec10,
                                                                          time_sec1,
                                                                          ub_data, ub_data_enemy, ub_data_value,
                                                                          characters_find, find_id, find_count)

                        if ub_result:
                            # update count
                            time_count = update_count(frame_rate, find_id, cap_interval)

                        elif is_normal_speed:
                            # check enemy ub
                            analyze_enemy_ub(time_count, work_frame, find_time, ub_data_enemy)

                    # check score existence
                    ret = analyze_score_frame(work_frame, SCORE_DATA, score_roi)

                    if ret is True:
                        # analyze total damage
                        ret = analyze_damage_frame(original_frame, damage_data_roi, tmp_damage)

                        if ret is True:
                            total_damage = "".join(tmp_damage)

                        break

    video.release()
    cm.clear_path(movie_path)

    # post-processing to timeline
    if len(ub_data_enemy) != 0 and ENEMY_UB in ub_data_enemy[-1]:
        ub_data_enemy.pop()

    debuff_value = ac.make_ub_value_list(ub_data_value, characters_find)

    time_result = tm.time() - start_time
    time_data.append("動画時間 : {:.3f}".format(frame_count / frame_rate) + "  sec")
    time_data.append("処理時間 : {:.3f}".format(time_result) + "  sec")

    status = get_analyze_status(ub_data, video_type)

    if status is not state.DONE:
        ub_data_enemy = False

    return ub_data, ub_data_enemy, time_data, total_damage, debuff_value, status


def edit_frame(frame):
    """edit frame to analyzable frame

    rgb 2 gray
    thresh frame color
    bitwise color

    Args
        frame (ndarray): original frame from movie

    Returns
        work_frame (ndarray): edited frame


    """
    work_frame = frame

    work_frame = cv2.cvtColor(work_frame, cv2.COLOR_RGB2GRAY)
    work_frame = cv2.threshold(work_frame, FRAME_THRESH, 255, cv2.THRESH_BINARY)[1]
    work_frame = cv2.bitwise_not(work_frame)

    return work_frame


def expand_frame(frame):
    """expand sd frame to hd frame size

    360p -> 720p
    640x360 -> 1280x720

    * now only 16:9 resolution support

    Args
        frame (ndarray): original frame from movie

    Returns
        work_frame (ndarray): expand frame


    """
    work_frame = frame

    work_frame = cv2.resize(work_frame, dsize=(FRAME_RESOLUTION[RESOLUTION_16_9]))

    return work_frame


def analyze_ub_frame(frame, roi, time_min, time_10sec, time_sec, ub_data, ub_data_enemy, ub_data_value,
                     characters_find, past_id, past_count):
    """analyze frame to find ub name

    analyze ub name roi and find best match character
    if 5 characters found, then search only these 5.

    Args
        frame (ndarray): edited frame from movie
        roi (list): search roi
        time_min (string): minute value
        time_10sec (string): 10 sec value
        time_sec (string): 1 sec value
        ub_data (list): ub name data
        ub_data_enemy (list): ub name data with enemy ub
        ub_data_value (list): founded ub data
        characters_find (list): founded characters
        past_id (int): find characters id
        past_count (int): find one character id time

    Returns
        ub_result (string): ub FOUND or NOT_FOUND
        find_id (int): find characters id
        find_count (int): find one character id time


    """
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    characters_num = len(CHARACTERS)
    ub_result = NOT_FOUND
    find_id = -1
    find_count = 0
    tmp_character = [False, 0]
    tmp_value = UB_THRESH

    if len(characters_find) < 5:
        # all characters search
        for j in range(characters_num):
            result_temp = cv2.matchTemplate(analyze_frame, CHARACTERS_DATA[j], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
            if max_val > tmp_value:
                # better match character found
                tmp_character = [CHARACTERS[j], j]
                tmp_value = max_val
                ub_result = FOUND
                find_id = j

        if ub_result is FOUND:
            tl = time_min + ":" + time_10sec + time_sec + " " + tmp_character[0]
            if len(ub_data) != 0 and ub_data[-1] == tl:
                # same time, same ub ignore
                find_count = past_count + 1
                return NOT_FOUND, find_id, find_count

            if find_id == past_id and past_count < 5:
                # in 50f time, same ub ignore
                find_count = past_count + 1
                return NOT_FOUND, find_id, find_count

            ub_data.append(tl)
            ub_data_enemy.append(tl)
            ub_data_value.extend([[int(int(time_min) * 60 + int(time_10sec) * 10 + int(time_sec)), tmp_character[1]]])
            if tmp_character[1] not in characters_find:
                characters_find.append(tmp_character[1])

            return FOUND, find_id, find_count
    else:
        for j in range(5):
            # 5 characters search
            result_temp = cv2.matchTemplate(analyze_frame, CHARACTERS_DATA[characters_find[j]], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
            if max_val > tmp_value:
                # better match character found, update
                tmp_character = [CHARACTERS[characters_find[j]], characters_find[j]]
                tmp_value = max_val
                ub_result = FOUND
                find_id = characters_find[j]

        if ub_result is FOUND:
            tl = time_min + ":" + time_10sec + time_sec + " " + tmp_character[0]
            if len(ub_data) != 0 and ub_data[-1] == tl:
                # same time, same ub ignore
                find_count = past_count + 1
                return NOT_FOUND, find_id, find_count

            if find_id == past_id and past_count < 5:
                # in 50f time, same ub ignore
                find_count = past_count + 1
                return NOT_FOUND, find_id, find_count

            ub_data.append(tl)
            ub_data_enemy.append(tl)
            ub_data_value.extend([[int(int(time_min) * 60 + int(time_10sec) * 10 + int(time_sec)), tmp_character[1]]])

            return FOUND, find_id, find_count

    return NOT_FOUND, find_id, find_count


def analyze_timer_frame(frame, roi, data_num, time_data):
    """analyze frame to find timer name

    analyze timer roi and find best match time
    min, 10 sec, 1sec values search

    Args
        frame (ndarray): edited frame from movie
        roi (list): search roi
        data_num (int): number of digits
        time_data (string): now min, 10sec, 1sec

    Returns
        tmp_number (string): timer number


    """
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    tmp_number = time_data
    tmp_value = TIMER_THRESH

    for j in range(data_num):
        result_temp = cv2.matchTemplate(analyze_frame, SEC_DATA[j], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
        if max_val > tmp_value:
            tmp_number = NUMBERS[j]
            tmp_value = max_val

    return tmp_number


def analyze_menu_frame(frame, menu, roi):
    """check menu button

    found menu button for start analyze

    Args
        frame (ndarray): edited frame from movie
        menu (ndarray): MENU template
        roi (list): search roi

    Returns
        True, False (boolean): menu found or not
        max_loc (list, boolean): menu position or False


    """
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    result_temp = cv2.matchTemplate(analyze_frame, menu, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
    if max_val > MENU_THRESH:
        return True, max_loc

    return False, None


def analyze_score_frame(frame, score, roi):
    """check score

    found score for end analyze

    Args
        frame (ndarray): edited frame from movie
        score (ndarray): score template
        roi (list): search roi

    Returns
        True, False (boolean): score found or not


    """
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    result_temp = cv2.matchTemplate(analyze_frame, score, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
    if max_val > MENU_THRESH:
        return True

    return False


def analyze_damage_frame(frame, roi, damage):
    """analyze total damage

    find total damage

    Args
        frame (ndarray): original frame from movie
        roi (list): search roi
        damage (list): damage input list

    Returns
        ret (boolean): total score found or not found


    """
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    analyze_frame = cv2.cvtColor(analyze_frame, cv2.COLOR_BGR2HSV)
    analyze_frame = cv2.inRange(analyze_frame, np.array([10, 120, 160]), np.array([40, 255, 255]))

    # find score position list
    find_list = find_damage_loc(analyze_frame)

    # sort score position ascending order
    find_list.sort()

    # create damage information
    ret = make_damage_list(find_list, damage)

    return ret


def analyze_anna_icon_frame(frame, roi, characters_find):
    """search anna frame

    check anna icon
    anna sometimes does not use UB

    Args
        frame (ndarray): edited frame from movie
        roi (list): search roi
        characters_find (list): characters find list

    Returns


    """
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    icon_num = len(ICON_DATA)

    for j in range(icon_num):
        result_temp = cv2.matchTemplate(analyze_frame, ICON_DATA[j], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
        if max_val > ICON_THRESH:
            characters_find.append(CHARACTERS.index("アンナ"))

    return


def find_damage_loc(frame):
    """find damage position

    find damage position to total damage
    difference 5 pixels to classify as the same position

    Args
        frame (ndarray): edited frame from movie
    Returns
        find_list (list): total score found or not found


    """
    find_list = []
    number_num = len(NUMBERS)

    for i in range(number_num):
        # find position
        result_temp = cv2.matchTemplate(frame, DAMAGE_DATA[i], cv2.TM_CCOEFF_NORMED)
        loc = np.where(result_temp > DAMAGE_THRESH)[1]
        result_temp = result_temp.T

        # delete duplication and sort ascending order
        loc = list(set(loc))
        sort_loc = sorted(np.sort(loc))

        loc_number = len(sort_loc)

        # store number by position
        if loc_number == 0:
            # no position found
            find_list.append([0, i, 0])
        elif loc_number == 1:
            # 1 position found
            find_list.append([sort_loc[0], i, max(result_temp[sort_loc[0]])])
        else:
            # multiple position found
            temp_loc = sort_loc[0]
            temp_value = max(result_temp[sort_loc[0]])

            # difference 5 pixels to classify as the same position
            for j in range(loc_number - 1):

                if sort_loc[j + 1] > sort_loc[j] + 5:
                    # more than 5 pixels different position
                    find_list.append([temp_loc, i, temp_value])
                    temp_loc = sort_loc[j + 1]
                    temp_value = max(result_temp[sort_loc[j + 1]])

                else:
                    # in 5 pixels different position
                    value_after = max(result_temp[sort_loc[j + 1]])

                    if value_after > temp_value:
                        # better match damage found, update value
                        temp_loc = sort_loc[j + 1]
                        temp_value = value_after

            find_list.append([temp_loc, i, temp_value])

    return find_list


def make_damage_list(find_list, damage):
    """make damage list

    from result, make damage date to list

    Args
        find_list (list): score data, as raw data
    Returns
        ret (boolean): damage found or not found


    """
    ret = False
    temp_list = []

    list_num = len(find_list)

    # from result, delete same position
    for i in range(list_num):
        if find_list[i][0] != 0:
            if not temp_list:
                temp_list = find_list[i]
                ret = True

            if find_list[i][0] > temp_list[0] + 5:
                # different position
                damage.append(str(temp_list[1]))
                temp_list = find_list[i]

            else:
                # difference 5 pixels to classify as the same position
                if find_list[i][2] > temp_list[2]:
                    # better match damage found, update value
                    temp_list = find_list[i]

    if ret is True:
        damage.append(str(temp_list[1]))

    return ret


def get_analyze_status(ub_data, video_type):
    """get video analyze status

    make analyze status from
    timeline existence and video_resolution(HD / SD)

    Args
        ub_data (list): timeline list
        video_type (list): score data, as raw data
    Returns
        status (int): error status


    """
    if ub_data:
        # found timeline
        if video_type is RESOLUTION_16_9_SD:
            status = state.TMP_DONE_IN_SD
        else:
            status = state.DONE
    else:
        # not found timeline
        if video_type is RESOLUTION_16_9_SD:
            status = state.TMP_INCOMPLETE_IN_SD
        else:
            status = state.ERR_INCOMPLETE_IN_HD

    return status


def time_check(time_min, time_sec10, time_sec1, past_time):
    now_time = int(time_min) * 60 + int(time_sec10) * 10 + int(time_sec1)
    if past_time != now_time:
        return now_time, False
    else:
        return now_time, True


def update_count(frame_rate, find_id, cap_interval):
    """update count after friendly ub


    Args
        frame_rate (int): movie fps
        find_id (int): find character id
        cap_interval (int): read frame interval


    Returns
        time_count (int): ub interval

    """
    return -1 * (frame_rate / 30) * int(cd.ub_time_table[find_id] / cap_interval)


def check_enemy_ub(time_count):
    """check enemy ub


    Args
        time_count (int): count up after ub


    Returns
        is_enemy_ub (boolean): enemy ub existence

    """
    if time_count > 9:
        return True
    else:
        return False


def analyze_enemy_ub(time_count, work_frame, find_time, ub_data_enemy):
    """analyze enemy ub


    Args
        time_count (int): count up after ub
        work_frame (ndarray): expand frame
        find_time (string): m:ss
        ub_data_enemy (list): found ub data with enemy ub


    Returns

    """
    # check enemy ub
    is_enemy_ub = check_enemy_ub(time_count)
    if is_enemy_ub:
        menu_check = analyze_menu_frame(work_frame, MENU_DATA, MENU_ROI)[0]
        if menu_check:
            tl = find_time + " " + ENEMY_UB
            if len(ub_data_enemy) != 0 and ub_data_enemy[-1] != tl:
                # same time, same ub ignore
                ub_data_enemy.append(tl)


def analyze_speed(frame, roi):
    """analyze speed

    check speed icon for get speed

    Args
        frame (ndarray): original frame from movie
        roi (list): search roi

    Returns
        ret (boolean): find or not find speed up (x2 / x4) icon inactive


    """
    analyze_frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    analyze_frame = cv2.cvtColor(analyze_frame, cv2.COLOR_RGB2GRAY)
    analyze_frame = cv2.threshold(analyze_frame, SPEED_ICON_THRESH, 255, cv2.THRESH_BINARY)[1]
    analyze_frame = cv2.bitwise_not(analyze_frame)

    speed_num = len(SPEED_DATA)

    for j in range(speed_num):
        result_temp = cv2.matchTemplate(analyze_frame, SPEED_DATA[j], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_temp)
        if max_val > SPEED_THRESH:
            # find speed up (x2 / x4) icon active
            return False

    return True
