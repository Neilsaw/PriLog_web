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
import state_list as state
import datetime


# cache max number
CACHE_ELMS = 7


def save_cache(youtube_id, title, time_line, time_line_enemy, time_data, total_damage, debuff_value, status):
    """save cache

    save cache if cache not found

    save cache if before cache is tmp sd analyze

    change status if before and now status are same

    Args:
        youtube_id (string): youtube id
        title (string): youtube movie title
        time_line (list, boolean): found ub data or False
        time_line_enemy (list, boolean): found ub data with enemy data or False
        time_data (list, boolean): spend time while analyze or False
        total_damage (string, boolean): total damage or False
        debuff_value (list, boolean): ub timing debuff values or False
        status (int): error status

    Returns:
        status (int): error status


    """
    past_status = cache_status_check(youtube_id)
    present_status = status
    if past_status is False:

        json.dump([title, time_line, time_line_enemy, time_data, total_damage, debuff_value, present_status],
                  open(ap.cache_dir + urllib.parse.quote(youtube_id) + ".json", "w"))

    else:
        result, present_status = status_comparison(past_status, status)
        if result is True:

            json.dump([title, time_line, time_line_enemy, time_data, total_damage, debuff_value, present_status],
                      open(ap.cache_dir + urllib.parse.quote(youtube_id) + ".json", "w"))

    return present_status


def cache_check(youtube_id):
    """cache check with youtube_id

    search cache and get cache data
    cache: (6)
    [title, time_line, time_data, total_damage, debuff_value, status]

    Args:
        youtube_id (str): user input youtube_id

    Returns:
        status (int): cache or False


    """
    try:
        cache_path = ap.cache_dir + urllib.parse.quote(youtube_id) + ".json"
        ret = json.load(open(cache_path))
        if len(ret) is CACHE_ELMS:  # in case of number of cached elements is correct
            title, time_line, time_line_enemy, time_data, total_damage, debuff_value, past_status = ret
            if past_status // 100 == 3:

                if check_pass_time(cache_path, 300):  # through 3xx error if passed 5 minutes
                    return False
                else:
                    return ret
            else:
                return ret
        else:  # in case of number of cached elements is incorrect
            # delete cache
            clear_path(cache_path)
            return False

    except FileNotFoundError:
        # not found cache
        return False


def queue_cache_check(youtube_id):
    """cache check with youtube_id while queue

    search cache and get cache data
    cache: (6)
    [title, time_line, time_data, total_damage, debuff_value, status]

    Args:
        youtube_id (str): user input youtube_id

    Returns:
        status (int): cache or False


    """
    try:
        cache_path = ap.cache_dir + urllib.parse.quote(youtube_id) + ".json"
        ret = json.load(open(cache_path))
        if len(ret) is CACHE_ELMS:  # in case of number of cached elements is correct
            return ret

        else:  # in case of number of cached elements is incorrect
            return False

    except FileNotFoundError:
        # not found cache
        return False


def cache_status_check(youtube_id):
    """cache status check with youtube_id

    search cache and get cache data
    cache: (6)
    [title, time_line, time_data, total_damage, debuff_value, status]

    and if status is 3xx error, then return past status

    Args:
        youtube_id (str): user input youtube_id

    Returns:
        status (int, boolean): error status or False (in case of cache status is not 3xx)


    """
    try:
        cache_path = ap.cache_dir + urllib.parse.quote(youtube_id) + ".json"
        ret = json.load(open(cache_path))
        if len(ret) is CACHE_ELMS:  # in case of number of cached elements is correct
            past_status = ret[5]
            return past_status
        else:  # in case of number of cached elements is incorrect
            # not found cache
            return False

    except FileNotFoundError:
        # not found cache
        return False


def status_comparison(past, present):
    """status compares with past and present
    this function calls if valid cache exists


    Args:
        past (int): past analyze status (should be 3xx)
        present (int): present analyze status

    Returns:
        cacheable (boolean): cache is able to make or not
        set_status (int): chosen status by combination


    """

    # past status is 2xx/4xx return confirmed status
    if past // 100 == 2 or past // 100 == 4:
        return False, past

    # present status is 2xx/4xx return confirmed status
    if present // 100 == 2 or present // 100 == 4:
        return True, present

    # Only 3xx should go below but it dose not matter
    # past status is 30x and recently 3xx, do not update
    if not past % 100 // 10 and present % 100 // 10:
        return False, past

    # past status is 30x and recently 30x, fix as 20x
    elif not past % 100 // 10 and not present % 100 // 10:
        return True, present - 100

    # past status is 3xx and recently 30x, yield to try one more time
    elif not present % 100 // 10:
        return True, present

    # past status is 3xx and recently 3xx, fix as 4xx
    elif past % 100 // 10 and present % 100 // 10:
        return True, present + 100

    # all pattern should be covered on above, but just in case throw exception
    else:
        return True, 399


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


def is_path_due(path):
    """check path

    check path turn

    Args:
        path (str): analyze control file path

    Returns:
        True/False (boolean): oldest path:True secondly path:False


    """
    try:
        # get list queue file
        directory = os.path.dirname(path)
        fl = glob(directory + "/*")
        if not fl:
            return False

        # sort time stamp and find oldest queue
        fl.sort(key=lambda x: os.path.getctime(x))
        comp = fl[0].replace("\\", "/")
        if comp == path:
            return True
        else:
            return False
    except:
        return False


def is_path_exists(path):
    """check path

    check path existence

    Args:
        path (str): analyze control queue file path

    Returns:
        True/False (boolean): exist:True not found:False


    """
    try:
        directory = os.path.dirname(path)
        fl = os.listdir(directory + "/")
        if not fl:
            return False
        else:
            return True
    except:
        return False


def is_pending_download(margin):
    """check is download job ready

    check pending timestamp to download available
    for avoid too many query to YouTube

    Args:
        margin (int):

    Returns:
        result (boolean): True: ready to download / False: not ready


    """
    queue_path = ap.dl_pending_dir + "pending"

    result = False

    if os.path.exists(queue_path):
        if check_pass_time(queue_path, margin):
            clear_path(queue_path)
            result = True
    else:
        result = True

    return result


def watchdog(youtube_id, is_parent, margin, err_type):
    """check is job timeout

    check pending and queue timestamp to determine timeout

    Args:
        youtube_id: str
        is_parent: bool
        margin: int
        err_type: ERR_CODE

    Returns:
        None


    """
    queue_path = ap.queue_dir + str(youtube_id)
    pending_path = ap.pending_dir + str(youtube_id)

    if is_parent:
        job_path = pending_path
    else:
        job_path = queue_path

    if os.path.exists(job_path):
        if check_pass_time(job_path, margin):
            save_cache(youtube_id, "", False, False, False, False, False, err_type)
            clear_path(job_path)
            if is_parent:
                clear_path(queue_path)

    return


def watchdog_download(youtube_id, margin):
    """check is download job timeout

    check pending and queue timestamp to determine timeout

    Args:
        youtube_id: str
        margin: int

    Returns:
        True/False: boolean


    """
    queue_path = ap.dl_queue_dir + str(youtube_id)

    result = False

    if os.path.exists(queue_path):
        if check_pass_time(queue_path, margin):
            clear_path(queue_path)
            result = True

    return result


def tmp_movie_clear():
    """delete movie file

    delete oldest 1 movie file if its made 2 hours later

    this function is intended as every query

    Args:

    Returns:


    """
    try:
        fl = glob(ap.stream_dir + "/*")
        if not fl:
            return

        fl.sort(key=lambda x: os.path.getctime(x))

        if check_pass_time(fl[0], 7200):
            clear_path(fl[0])

    except FileNotFoundError:
        pass


def check_pass_time(file_path, thresh):
    """check time

    check file update time with current time


    Args:
        file_path (str): time as datetime
        thresh (int): thresh value "seconds" for check

    Returns:
        True (boolean): passed time or file not found
        False (boolean): not passed time


    """
    now = datetime.datetime.today()
    try:
        timestamp = datetime.datetime.fromtimestamp(int(os.path.getmtime(file_path)))
    except FileNotFoundError:
        return True

    if (now - timestamp).total_seconds() >= thresh:
        return True
    else:
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
