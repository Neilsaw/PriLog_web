# -*- coding: utf-8 -*-
"""error list

     * status code and error list


"""
import numpy as np


# Status Code
# 2xx Success
DONE = 200
DONE_IN_SD = 201

# 3xx Temporary Unable
TMP_DONE_IN_SD = 301
ERR_INCOMPLETE_IN_SD = 311
ERR_CANT_GET_HD = 312
ERR_ANALYZE_TIMEOUT = 313
ERR_TMP_UNEXPECTED = 399

# 4xx Confirmed Failure
ERR_INCOMPLETE_IN_HD = 410
ERR_BAD_URL = 412
ERR_BAD_LENGTH = 413
ERR_BAD_RESOLUTION = 414
ERR_PERM_UNEXPECTED = 499

# 5xx API Request Failure
ERR_BAD_REQ = 522
ERR_BAD_TOKEN = 523
ERR_REQ_UNEXPECTED = 599


error_list = [
    [DONE, "OK"],
    [DONE_IN_SD, "SD画質での解析です。"],
    [TMP_DONE_IN_SD, "SD画質での解析です。5分以上経過後に再度解析を試みられます。"],
    [ERR_INCOMPLETE_IN_SD, "SD画質での解析に失敗しました。5分以上経過後に再度解析を試みられます。"],
    [ERR_INCOMPLETE_IN_HD, "解析出来ない動画です。"],
    [ERR_CANT_GET_HD, "動画の取得に失敗しました。5分以上経過後に再度解析を試みられます。"],
    [ERR_ANALYZE_TIMEOUT, "解析がタイムアウトしました。5分以上経過後に再度解析を試みられます。"],
    [ERR_TMP_UNEXPECTED, "一時的に解析出来ません。5分以上経過後に再度解析を試みられます。"],
    [ERR_BAD_URL, "URLはhttps://www.youtube.com/watch?v=...の形式でお願いします。"],
    [ERR_BAD_LENGTH, "動画時間が長すぎるため、解析に対応しておりません。"],
    [ERR_BAD_RESOLUTION, "非対応の解像度です。720pの一部の動画に対応しております。"],
    [ERR_PERM_UNEXPECTED, "解析出来ない動画です。"],
    [ERR_BAD_REQ, "必須パラメータがありません。"],
    [ERR_BAD_TOKEN, "不正なトークンです。　twitter @PriLog_R までご連絡下さい。"],
    [ERR_REQ_UNEXPECTED, "API処理中に予期しない問題が起きました。　twitter @PriLog_R までご連絡下さい。"]
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
