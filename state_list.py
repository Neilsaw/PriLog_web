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
    [DONE, "OK", "(cfm) OK"],
    [DONE_IN_SD, "SD画質での解析です。", "(cfm) OK, but analyze in SD(360p)"],
    [TMP_DONE_IN_SD, "SD画質での解析です。5分以上経過後に再度解析を試みられます。", "(tmp) OK, but analyze in SD(360p)"],
    [TMP_INCOMPLETE_IN_SD, "SD画質での解析に失敗しました。5分以上経過後に再度解析を試みられます。",
     "(tmp) Failed to analyze in SD(360p)"],
    [TMP_CANT_GET_HD, "動画の取得に失敗しました。5分以上経過後に再度解析を試みられます。", "(tmp) Failed to get Movie"],
    [TMP_ANALYZE_TIMEOUT, "解析がタイムアウトしました。5分以上経過後に再度解析を試みられます。", "(tmp) Analyze timeout"],
    [TMP_QUEUE_TIMEOUT, "解析待機中にタイムアウトしました。5分以上経過後に再度解析を試みられます。", "(tmp) Queue timeout"],
    [TMP_UNEXPECTED, "一時的に解析出来ません。5分以上経過後に再度解析を試みられます。", "(tmp) Unexpected error"],
    [ERR_INCOMPLETE_IN_SD, "解析出来ない動画です。", "(cfm) Failed to analyze in SD(360p)"],
    [ERR_ANALYZE_TIMEOUT, "動画の解析中にタイムアウトしました。", "(cfm) Analyze timeout"],
    [ERR_QUEUE_TIMEOUT, "動画の解析待ち中にタイムアウトしました。", "(cfm) Queue timeout"],
    [ERR_INCOMPLETE_IN_HD, "TLが存在しない動画です。", "(cfm) No Timeline movie in HD(720p)"],
    [ERR_CANT_GET_HD, "解析出来ない動画です。", "(cfm) Failed to get Movie"],
    [ERR_BAD_URL, "URLはhttps://www.youtube.com/watch?v=...の形式でお願いします。", "Bad movie url"],
    [ERR_BAD_LENGTH, "動画時間が長すぎるため、解析に対応しておりません。", "(cfm) Too long movie length"],
    [ERR_BAD_RESOLUTION, "非対応の解像度です。720pの一部の動画に対応しております。", "(cfm) Bad movie resolution"],
    [ERR_COPYRIGHTED_CONTENT, "著作権で保護されているため、動画の取得ができません。", "(cfm) Can not download movie"],
    [ERR_PRIVATE_DELETED_CONTENT, "非公開または削除されたため、動画の取得ができません。", "(cfm) Can not download movie"],
    [ERR_UNAVAILABLE_CONTENT, "ライブ配信または現在公開されていないため、動画の取得ができません。",
     "(cfm) Can not download movie"],
    [ERR_PERM_UNEXPECTED, "解析出来ない動画です。", "(cfm) Unexpected error"],
    [ERR_APP_SERVER_URL, "解析サーバーへのエラーが発生しました。", "Server error"],
    [ERR_APP_SERVER_HTTP, "解析サーバーへのエラーが発生しました。", "Server error"],
    [ERR_BAD_REQ, "必須パラメータがありません。", "No url on rest"],
    [ERR_BAD_TOKEN, "不正なトークンです。　Twitter @PriLog_R までご連絡下さい。",
     "Invalid token, please contact me on Twitter @PriLog_R"],
    [ERR_SERVICE_UNAVAILABLE, "申し訳ありません。現在サーバー側の問題により解析ができません。", "Server error"],
    [ERR_REQ_UNEXPECTED, "API処理中に予期しない問題が起きました。　Twitter @PriLog_R までご連絡下さい。",
     "(cfm) Unexpected error"]
]


def get_error_message(error_type, language=1):
    """get error_message with args

    Args:
        error_type (int): error_type
        language (int): message language 1: Japanese, 2: English

    Returns:
        error (str): error_message get from error_list


    """

    arr = np.array(error_list)
    pos = np.argwhere(arr == str(error_type))
    try:
        error = error_list[pos[0][0]][language]
    except IndexError:
        # エラーステータス改訂時に過去のキャッシュ参照した場合または予期しないエラーの場合
        error = error_list[-1][language]

    return error
