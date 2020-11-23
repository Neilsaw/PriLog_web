# -*- coding: utf-8 -*-
import sys
import analyze as al
import common as cm
import app as ap


def do_analyze():
    # 変数不足時は終了
    if not sys.argv[1]:
        return

    youtube_url = sys.argv[1]

    # ID部分の取り出し
    youtube_id = al.get_youtube_id(youtube_url)
    if not youtube_id:
        return

    queue_path = ap.queue_dir + str(youtube_id)
    pending_path = ap.pending_dir + str(youtube_id)

    cached = cm.cache_check(youtube_id)

    # 5分経過した3xx キャッシュ以外は再解析しない
    if cached:
        cm.clear_path(queue_path)
        cm.clear_path(pending_path)
        return

    # youtube動画検索/検証
    path, title, length, thumbnail, url_result = al.search(youtube_id)
    if url_result % 100 // 10 == 2:
        cm.save_cache(youtube_id, title, False, False, False, False, False, url_result)
    else:
        # TL解析
        time_line, time_line_enemy, time_data, total_damage, debuff_value, analyze_result = al.analyze_movie(path)
        # キャッシュ保存
        cm.save_cache(youtube_id, title, time_line, time_line_enemy, False, total_damage, debuff_value, analyze_result)

    cm.clear_path(queue_path)
    cm.clear_path(pending_path)


if __name__ == "__main__":
    do_analyze()
