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
TMP_INCOMPLETE_IN_SD = 311
TMP_ANALYZE_TIMEOUT = 313
TMP_QUEUE_TIMEOUT = 314
TMP_CANT_GET_HD = 322
TMP_UNEXPECTED = 399

# 4xx Confirmed Failure
ERR_INCOMPLETE_IN_SD = 411
ERR_ANALYZE_TIMEOUT = 413
ERR_QUEUE_TIMEOUT = 414
ERR_INCOMPLETE_IN_HD = 420
ERR_CANT_GET_HD = 422
ERR_BAD_URL = 423
ERR_BAD_LENGTH = 424
ERR_BAD_RESOLUTION = 425
ERR_COPYRIGHTED_CONTENT = 426
ERR_PRIVATE_DELETED_CONTENT = 427
ERR_UNAVAILABLE_CONTENT = 428
ERR_PERM_UNEXPECTED = 499

# 5xx API Request Failure
ERR_APP_SERVER_URL = 520
ERR_APP_SERVER_HTTP = 521
ERR_BAD_REQ = 532
ERR_BAD_TOKEN = 533
ERR_SERVICE_UNAVAILABLE = 544
ERR_REQ_UNEXPECTED = 599


error_list = [
    [DONE, "OK"],
    [DONE_IN_SD, "SD画質での解析です。"],
    [TMP_DONE_IN_SD, "SD画質での解析です。5分以上経過後に再度解析を試みられます。"],
    [TMP_INCOMPLETE_IN_SD, "SD画質での解析に失敗しました。5分以上経過後に再度解析を試みられます。"],
    [TMP_CANT_GET_HD, "動画の取得に失敗しました。5分以上経過後に再度解析を試みられます。"],
    [TMP_ANALYZE_TIMEOUT, "解析がタイムアウトしました。5分以上経過後に再度解析を試みられます。"],
    [TMP_QUEUE_TIMEOUT, "解析待機中にタイムアウトしました。5分以上経過後に再度解析を試みられます。"],
    [TMP_UNEXPECTED, "一時的に解析出来ません。5分以上経過後に再度解析を試みられます。"],
    [ERR_INCOMPLETE_IN_SD, "解析出来ない動画です。"],
    [ERR_ANALYZE_TIMEOUT, "動画の解析中にタイムアウトしました。"],
    [ERR_QUEUE_TIMEOUT, "動画の解析待ち中にタイムアウトしました。"],
    [ERR_INCOMPLETE_IN_HD, "TLが存在しない動画です。"],
    [ERR_CANT_GET_HD, "解析出来ない動画です。"],
    [ERR_BAD_URL, "URLはhttps://www.youtube.com/watch?v=...の形式でお願いします。"],
    [ERR_BAD_LENGTH, "動画時間が長すぎるため、解析に対応しておりません。"],
    [ERR_BAD_RESOLUTION, "非対応の解像度です。720pの一部の動画に対応しております。"],
    [ERR_COPYRIGHTED_CONTENT, "著作権で保護されているため、動画の取得ができません。"],
    [ERR_PRIVATE_DELETED_CONTENT, "非公開または削除されたため、動画の取得ができません。"],
    [ERR_UNAVAILABLE_CONTENT, "ライブ配信または現在公開されていないため、動画の取得ができません。"],
    [ERR_PERM_UNEXPECTED, "解析出来ない動画です。"],
    [ERR_APP_SERVER_URL, "解析サーバーへのエラーが発生しました。"],
    [ERR_APP_SERVER_HTTP, "解析サーバーへのエラーが発生しました。"],
    [ERR_BAD_REQ, "必須パラメータがありません。"],
    [ERR_BAD_TOKEN, "不正なトークンです。　Twitter @PriLog_R までご連絡下さい。"],
    [ERR_SERVICE_UNAVAILABLE, "申し訳ありません。現在サーバー側の問題により解析ができません。"],
    [ERR_REQ_UNEXPECTED, "API処理中に予期しない問題が起きました。　Twitter @PriLog_R までご連絡下さい。"]
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
    try:
        error = error_list[pos[0][0]][1]
    except IndexError:
        # エラーステータス改訂時に過去のキャッシュ参照した場合に発生する
        error = error_list[-1][1]

    return error
