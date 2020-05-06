# -*- coding: utf-8 -*-
"""common module app and analyze

     * cache check
     * queue flow control
     * get youtube_id


"""
import os
import json
from glob import glob
import urllib.parse
import app as ap
import error_list as el


# cache max number
CACHE_NUM = 6


def save_cache(youtube_id, title, time_line, time_data, total_damage, debuff_value, status):
    """save cache

    save cache if cache not found

    save cache if previous cache was tmp sd analyze

    Args:
        youtube_id (string): youtube id
        title (string): youtube movie title
        time_line (list, boolean): found ub data or False
        time_data (list, boolean): spend time while analyze or False
        total_damage (string, boolean): total damage or False
        debuff_value (list, boolean): ub timing debuff values or False
        status (int): error status

    Returns:


    """
    cache = cache_check(youtube_id)
    if cache is False:

        json.dump([title, time_line, time_data, total_damage, debuff_value, status],
                  open(ap.cache_dir + urllib.parse.quote(youtube_id) + ".json", "w"))

    elif cache[5] == el.TMP_DONE_IN_SD:

        if status is el.TMP_DONE_IN_SD:
            status = el.DONE_IN_SD

        json.dump([title, time_line, time_data, total_damage, debuff_value, status],
                  open(ap.cache_dir + urllib.parse.quote(youtube_id) + ".json", "w"))


def cache_check(youtube_id):
    """cache check with youtube_id

    search cache and get cache data
    cache: (6)
    [title, time_line, time_data, total_damage, debuff_value, status]

    Args:
        youtube_id (str): user input youtube_id

    Returns:
        ret (list, boolean): cache or False


    """
    try:
        cache_path = ap.cache_dir + urllib.parse.quote(youtube_id) + ".json"
        ret = json.load(open(cache_path))
        if len(ret) is CACHE_NUM:
            # cache elements count is control value
            return ret
        else:
            # cache elements count is not control value
            # delete cache
            clear_path(cache_path)
            return False

    except FileNotFoundError:
        # not found cache
        return False


def queue_append(path):
    """analyze queue append to file

    control analyze queue to download only one file

    Args:
        path (str): analyze control queue file path

    Returns:


    """
    try:
        with open(path, mode="w"):
            pass
    except FileExistsError:
        pass

    return


def pending_append(path):
    """pending append to file

    control pending queue to analyze only one file

    Args:
        path (str): analyze pending file path

    Returns:


    """
    try:
        with open(path, mode="w"):
            pass
    except FileExistsError:
        pass

    return


def is_queue_current(queue_path):
    """check queue

    check queue and check queue turn

    Args:
        queue_path (str): analyze control queue file path

    Returns:
        True/False (boolean): oldest queue:True secondly queue:False


    """
    try:
        # get list queue file
        fl = glob(ap.queue_dir + "*")

        # sort time stamp and find oldest queue
        fl.sort(key=lambda x: os.path.getctime(x))
        comp = fl[0].replace("\\", "/")
        if comp == queue_path:
            return True
        else:
            return False
    except:
        return False


def is_pending_exists():
    """check pending

    check pending and check pending existence

    Args:

    Returns:
        True/False (boolean): exist:True not found:False


    """
    try:
        fl = os.listdir(ap.pending_dir)
        if not fl:
            return False
        else:
            return True
    except:
        return False


def clear_path(path):
    """delete file

    delete file safely

    Args:
        path (str): file path

    Returns:


    """
    try:
        os.remove(path)
    except PermissionError:
        pass
    except FileNotFoundError:
        pass
    except TypeError:
        pass

    return
