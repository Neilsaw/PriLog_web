# -*- coding: utf-8 -*-
"""view module prilog application

     * view function, and run Flask




"""
from flask import Flask, render_template, request, session, redirect, jsonify
import os
import re
import datetime
import time as tm
import analyze as an
import common as cm
import error_list as el


# movie download directory
stream_dir = "tmp\\"
if not os.path.exists(stream_dir):
    os.mkdir(stream_dir)

# analyze result save as cache directory
cache_dir = "cache\\"
if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)

# save analyzing id as file directory
pending_dir = "pending\\"
if not os.path.exists(pending_dir):
    os.mkdir(pending_dir)

# waiting analyze id as file directory
queue_dir = "queue\\"
if not os.path.exists(queue_dir):
    os.mkdir(queue_dir)


def get_web_txt(youtube_id, title, time_line, debuff_value, total_damage):
    debuff_dict = None
    if debuff_value:
        debuff_dict = ({key: val for key, val in zip(time_line, debuff_value)})
    data_url = "https://prilog.jp/?v=" + youtube_id
    data_txt = "@PriLog_Rより%0a"
    data_txt += title + "%0a"
    if total_damage:
        total_damage = "総ダメージ " + "".join(total_damage)
        data_txt += total_damage + "%0a"

    return debuff_dict, data_txt, data_url, total_damage


def get_rest_result(title, time_line, time_data, total_damage, debuff_value):
    rest_result = {"title": title, "timeline": time_line, "process_time": time_data, "total_damage": total_damage,
                   "debuff_value": debuff_value, "timeline_txt": "\r\n".join(time_line)}

    if debuff_value:
        rest_result["timeline_txt_debuff"] = "\r\n".join(list(
            map(lambda x: "↓{} {}".format(str(debuff_value[x[0]][0:]).rjust(3, " "), x[1]),
                enumerate(time_line))))

    return rest_result


app = Flask(__name__)
app.config.from_object(__name__)
app.config["SECRET_KEY"] = "zJe09C5c3tMf5FnNL09C5e6SAzZuY"
app.config["JSON_AS_ASCII"] = False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = (request.form["Url"])

        # urlからid部分の抽出
        youtube_id = an.get_youtube_id(url)
        if youtube_id is False:
            error = el.get_error_message(el.ERR_BAD_URL)
            return render_template("index.html", error=error)

        cache = cm.cache_check(youtube_id)

        if cache is not False:
            title, time_line, time_data, total_damage, debuff_value, past_status = cache
            if past_status // 100 == 2:
                debuff_dict, data_txt, data_url, total_damage = get_web_txt(youtube_id, title,
                                                                            time_line, debuff_value, total_damage)

                return render_template("result.html", title=title, timeLine=time_line,
                                       timeData=time_data, totalDamage=total_damage, debuffDict=debuff_dict,
                                       data_txt=data_txt, data_url=data_url)

            elif past_status // 100 == 3:
                pass
            else:
                error = el.get_error_message(past_status)
                return render_template("index.html", error=error)

        path, title, length, thumbnail, url_result = an.search(youtube_id)

        if url_result // 100 == 4:
            error = el.get_error_message(url_result)
            cm.save_cache(youtube_id, title, False, False, False, False, url_result)
            return render_template("index.html", error=error)

        elif url_result == el.ERR_CANT_GET_HD:
            error = el.get_error_message(url_result)
            return render_template("index.html", error=error)

        session["path"] = path
        session["title"] = title
        session["youtube_id"] = youtube_id
        length = int(int(length) / 8) + 3

        return render_template("analyze.html", title=title, length=length, thumbnail=thumbnail)

    elif request.method == "GET":
        if "v" in request.args:  # ?v=YoutubeID 形式のGETであればリザルト返却
            youtube_id = request.args.get("v")
            if re.fullmatch(r"^([a-zA-Z0-9_-]{11})$", youtube_id):
                cache = cm.cache_check(youtube_id)
                if cache is not False:
                    title, time_line, time_data, total_damage, debuff_value, past_status = cache
                    if past_status // 100 == 2:
                        debuff_dict, data_txt, data_url, total_damage = get_web_txt(youtube_id, title,
                                                                                    time_line, debuff_value,
                                                                                    total_damage)

                        return render_template("result.html", title=title, timeLine=time_line,
                                               timeData=time_data, totalDamage=total_damage, debuffDict=debuff_dict,
                                               data_txt=data_txt, data_url=data_url)

                    elif past_status // 100 == 3:
                        pass

                    else:
                        error = el.get_error_message(past_status)
                        return render_template("index.html", error=error)

                else:  # キャッシュが存在しない場合は解析
                    path, title, length, thumbnail, url_result = an.search(youtube_id)

                    if url_result // 100 == 4:
                        error = el.get_error_message(url_result)
                        cm.save_cache(youtube_id, title, False, False, False, False, url_result)
                        return render_template("index.html", error=error)

                    elif url_result == el.ERR_CANT_GET_HD:
                        error = el.get_error_message(url_result)
                        return render_template("index.html", error=error)

                    session["path"] = path
                    session["title"] = title
                    session["youtube_id"] = youtube_id
                    length = int(int(length) / 8) + 3

                    return render_template("analyze.html", title=title, length=length, thumbnail=thumbnail)

            else:  # prilog.jp/(YoutubeID)に該当しないリクエスト
                error = "不正なリクエストです"
                return render_template("index.html", error=error)
            
        else:
            path = session.get("path")
            session.pop("path", None)
            session.pop("title", None)
            session.pop("youtube_id", None)

            error = None
            if path is el.ERR_BAD_RESOLUTION:
                error = el.get_error_message(path)

            elif path is not None:
                cm.clear_path(path)

            return render_template("index.html", error=error)


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    path = session.get("path")
    title = session.get("title")
    youtube_id = session.get("youtube_id")
    session.pop("path", None)

    if request.method == "GET" and path is not None:
        # TL解析
        time_line, time_data, total_damage, debuff_value, status = an.analyze_movie(path)

        # キャッシュ保存
        cm.save_cache(youtube_id, title, time_line, False, total_damage, debuff_value, status)

        if status % 100 // 10 == 0:
            # 解析が正常終了ならば結果を格納
            session["time_line"] = time_line
            session["time_data"] = time_data
            session["total_damage"] = total_damage
            session["debuff_value"] = debuff_value
            return render_template("analyze.html")
        else:
            session["path"] = el.ERR_BAD_RESOLUTION
            return render_template("analyze.html")
    else:
        return redirect("/")


@app.route("/result", methods=["GET", "POST"])
def result():
    title = session.get("title")
    time_line = session.get("time_line")
    time_data = session.get("time_data")
    total_damage = session.get("total_damage")
    debuff_value = session.get("debuff_value")
    youtube_id = session.get("youtube_id")
    session.pop("title", None)
    session.pop("time_line", None)
    session.pop("time_data", None)
    session.pop("total_damage", None)
    session.pop("debuff_value", None)
    session.pop("youtube_id", None)

    if request.method == "GET" and time_line is not None:
        debuff_dict, data_txt, data_url, total_damage = get_web_txt(youtube_id, title,
                                                                    time_line, debuff_value, total_damage)

        return render_template("result.html", title=title, timeLine=time_line,
                               timeData=time_data, totalDamage=total_damage, debuffDict=debuff_dict,
                               data_txt=data_txt, data_url=data_url)
    else:
        return redirect("/")


@app.route("/download", methods=["GET", "POST"])
def download():
    if request.method == "GET":
        return render_template("download.html")
    else:
        return redirect("/")


@app.route("/rest", methods=["GET", "POST"])
def rest():
    if request.method == "GET":
        return render_template("rest.html")
    else:
        return redirect("/")


@app.route("/rest/analyze", methods=["POST", "GET"])
def rest_analyze():
    status = el.DONE
    rest_result = {}
    ret = {}
    url = ""
    if request.method == "POST":
        if "Url" not in request.form:
            status = el.ERR_BAD_REQ

            ret["result"] = rest_result
            ret["msg"] = el.get_error_message(status)
            ret["status"] = status
            return jsonify(ret)
        else:
            url = request.form["Url"]

    elif request.method == "GET":
        if "Url" not in request.args:
            status = el.ERR_BAD_REQ

            ret["result"] = rest_result
            ret["msg"] = el.get_error_message(status)
            ret["status"] = status
            return jsonify(ret)
        else:
            url = request.args.get("Url")

    # キャッシュ確認
    youtube_id = an.get_youtube_id(url)
    if youtube_id is False:
        # 不正なurlの場合
        status = el.ERR_BAD_URL
    else:
        # 正常なurlの場合
        cache = cm.cache_check(youtube_id)

        if cache is not False:
            # キャッシュ有りの場合
            # キャッシュを返信
            title, time_line, time_data, total_damage, debuff_value, past_status = cache
            if past_status // 100 == 2:
                rest_result = get_rest_result(title, time_line, time_data, total_damage, debuff_value)

                ret["result"] = rest_result
                ret["msg"] = el.get_error_message(past_status)
                ret["status"] = past_status
                return jsonify(ret)

            elif (past_status // 100) == 3:
                pass
            else:
                ret["result"] = rest_result
                ret["msg"] = el.get_error_message(past_status)
                ret["status"] = past_status
                return jsonify(ret)

        # start analyze
        # 既にキューに登録されているか確認
        queue_path = queue_dir + str(youtube_id)
        pending_path = pending_dir + str(youtube_id)
        queued = os.path.exists(queue_path)
        if queued:  # 既に解析中の場合
            while True:  # キューが消えるまで監視
                # 暫定的実装
                # 監視中にキューが30分以上残置されているのを見つけると削除する
                try:
                    now = datetime.date.today()  # 現在の時刻を取得
                    timestamp = datetime.date.fromtimestamp(int(os.path.getmtime(queue_path)))

                    if (now - timestamp).seconds >= 30 * 60:  # 30分経過してたら削除
                        cm.clear_path(queue_path)
                        cm.clear_path(pending_path)

                except FileNotFoundError:
                    pass

                queued = os.path.exists(queue_path)
                if queued:
                    tm.sleep(1)
                    continue
                else:  # 既に開始されている解析が完了したら、そのキャッシュJSONを返す
                    cache = cm.cache_check(youtube_id)
                    if cache is not False:
                        title, time_line, time_data, total_damage, debuff_value, past_status = cache
                        if past_status // 100 == 2 or past_status // 100 == 3:
                            rest_result = get_rest_result(title, time_line, time_data, total_damage, debuff_value)

                        status = past_status
                        break
                    else:  # キャッシュ未生成の場合
                        # キャッシュを書き出してから解析キューから削除されるため、本来起こり得ないはずのエラー
                        status = el.ERR_UNEXPECTED
                        break

        else:  # 既に解析中ではない場合
            # 解析キューに登録
            cm.queue_append(queue_path)

            # キューが回ってきたか確認し、来たら解析実行
            while True:
                if not cm.is_pending_exists() and cm.is_queue_current(queue_path):
                    # pendingに登録
                    pending_path = pending_dir + str(youtube_id)
                    cm.pending_append(pending_path)
                    # youtube動画検索/検証
                    path, title, length, thumbnail, url_result = an.search(youtube_id)
                    status = url_result
                    if url_result // 100 == 4:
                        cm.save_cache(youtube_id, title, False, False, False, False, url_result)
                    elif url_result == el.ERR_CANT_GET_HD:
                        pass
                    else:
                        # TL解析
                        time_line, time_data, total_damage, debuff_value, analyze_result = an.analyze_movie(path)
                        status = analyze_result
                        # キャッシュ保存
                        cm.save_cache(youtube_id, title, time_line, False, total_damage, debuff_value, status)

                        if analyze_result is el.DONE:
                            # 解析が正常終了ならば結果を格納
                            rest_result = get_rest_result(title, time_line, time_data, total_damage, debuff_value)

                    cm.clear_path(queue_path)
                    cm.clear_path(pending_path)
                    break

                tm.sleep(1)

    ret["result"] = rest_result
    ret["msg"] = el.get_error_message(status)
    ret["status"] = status
    return jsonify(ret)


if __name__ == "__main__":
    app.run()
