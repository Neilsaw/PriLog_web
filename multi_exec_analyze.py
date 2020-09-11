# -*- coding: utf-8 -*-
import sys
import analyze as al
import common as cm
import app as ap
import state_list as state
import configparser
import urllib.request
from urllib.error import URLError, HTTPError
import json
import os

config = configparser.ConfigParser()
config.read("config.ini")

APP_SERVER_1 = config.get("rest", "app1")
APP_SERVER_2 = config.get("rest", "app2")


def is_server():
    if os.path.isfile(ap.dl_server_dir + "1"):
        cm.clear_path(ap.dl_server_dir + "1")
        cm.queue_append(ap.dl_server_dir + "2")
        return APP_SERVER_2
    else:
        cm.clear_path(ap.dl_server_dir + "2")
        cm.queue_append(ap.dl_server_dir + "1")
        return APP_SERVER_1


def do_analyze():
    # 変数不足時は終了
    if not sys.argv[1]:
        return

    youtube_url = sys.argv[1]

    # ID部分の取り出し
    youtube_id = al.get_youtube_id(youtube_url)
    if not youtube_id:
        return

    cached = cm.cache_check(youtube_id)

    # 5分経過した3xx キャッシュ以外は再解析しない
    if cached:
        return

    queue_path = ap.queue_dir + str(youtube_id)
    pending_path = ap.pending_dir + str(youtube_id)

    url = "http://" + is_server() + "/rest/analyze?Url=" + youtube_url

    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as res:
            body = json.load(res)

            title = body.get("result").get("title")
            time_line = body.get("result").get("timeline")
            time_line_enemy = body.get("result").get("timeline_enemy")
            total_damage = body.get("result").get("total_damage")
            debuff_value = body.get("result").get("debuff_value")
            url_result = body.get("status")
    except HTTPError:
        title = ""
        url_result = state.ERR_APP_SERVER_HTTP
    except URLError:
        title = ""
        url_result = state.ERR_APP_SERVER_URL
    except TimeoutError:
        title = ""
        url_result = state.ERR_ANALYZE_TIMEOUT

    if url_result % 100 // 10 == 2:
        cm.save_cache(youtube_id, title, False, False, False, False, False, url_result)
    else:
        # キャッシュ保存
        cm.save_cache(youtube_id, title, time_line, time_line_enemy, False, total_damage, debuff_value, url_result)

    cm.clear_path(queue_path)
    cm.clear_path(pending_path)


if __name__ == "__main__":
    do_analyze()
