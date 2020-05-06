# -*- coding: utf-8 -*-
"""error list

     * status code and error list


"""
import numpy as np


# status code
# 2xx success
DONE = 200
DONE_IN_SD = 201

# 3xx temporarily failure
TMP_DONE_IN_SD = 301
ERR_CANT_GET_HD = 312
ERR_ANALYZE_TIMEOUT = 313

# 4xx Definite failure
ERR_BAD_URL = 412
ERR_BAD_LENGTH = 413
ERR_BAD_RESOLUTION = 414
ERR_UNEXPECTED = 499

# 5xx api request failure
ERR_BAD_REQ = 522
ERR_BAD_TOKEN = 523


error_list = [
    [DONE, "OK"],
    [DONE_IN_SD, "SD画質での解析です"],
    [TMP_DONE_IN_SD, "SD画質での解析です。5分経過後に再度解析をお願いします"],
    [ERR_CANT_GET_HD, "動画の取得に失敗しました。もう一度入力をお願いしま"],
    [ERR_ANALYZE_TIMEOUT, "解析がタイムアウトしました。もう一度入力をお願いします"],
    [ERR_BAD_URL, "URLはhttps://www.youtube.com/watch?v=...の形式でお願いします"],
    [ERR_BAD_LENGTH, "動画時間が長すぎるため、解析に対応しておりません"],
    [ERR_BAD_RESOLUTION, "非対応の動画です。720pの一部の動画に対応しております"],
    [ERR_UNEXPECTED, "解析結果の取得に失敗しました"],
    [ERR_BAD_REQ, "必須パラメータがありません"],
    [ERR_BAD_TOKEN, "不正なトークンです　twitter @PriLog_R までご連絡下さい"]
]


def get_error_message(error_type):
    """get error_message with args

    Args:
        error_type (int): error_type

    Returns:
        error (str): error_message get from error_list


    """

    arr = np.array(error_list)
    pos = np.argwhere(arr == str(error_type))
    error = error_list[pos[0][0]][1]

    return error
