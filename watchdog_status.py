# -*- coding: utf-8 -*-
"""check cache status

     * check cache status
     * this file uses standalone


"""
import sys
import os
import json
import time
import subprocess
import configparser
from glob import glob

from state_list import get_error_message, DONE

config = configparser.ConfigParser()
config.read("config.ini")
MAIL_ADDRESS = config.get("general", "mail_address")

CACHE_PATH = "./cache"


def create_filter_caches(span):
    """filtered caches to cache list in span


    Args:
        span (int): cache check span

    Returns:
        filtered_cache_paths (list): cache paths in span


    """
    all_caches = glob(CACHE_PATH + "/*.json")
    if not all_caches:
        return False

    sorted_caches = sorted(all_caches, key=lambda x: os.path.getctime(x), reverse=True)

    filtered_cache_paths = []
    current_time = time.time()
    for cache in sorted_caches:
        cache_time = os.path.getctime(cache)
        if current_time - cache_time < span:
            filtered_cache_paths.append(cache)
        else:
            break

    return filtered_cache_paths


def create_cache_statuses(cache_paths):
    """create status list from cache_list


    Args:
        cache_paths (list): cache paths in span

    Returns:
        statuses (list): status list


    """
    statuses = []
    try:
        for cache in cache_paths:
            ret = json.load(open(cache))
            status = ret[-1]
            statuses.append(str(status))

    except FileNotFoundError:
        # not found cache
        return False

    return statuses


def create_count_statuses(statuses):
    """count status appeared times


    Args:
        statuses (list): status list

    Returns:
        status_counts (list): status key with appeared times


    """
    status_counts = {}

    for status in statuses:
        if status in status_counts:
            # already found, count up
            status_counts[status] += 1
        else:
            status_counts[status] = 1

    return status_counts


def create_messages(counts):
    """status counts to messages


    Args:
        counts (collection): status key with appeared times

    Returns:
        messages (list): messages


    """
    messages = []
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    sorted_keys = [key[0] for key in sorted_counts]

    if str(DONE) in sorted_keys:
        messages.append("Good")
    else:
        messages.append("*Careful*")

    for key in sorted_keys:
        error_message = get_error_message(int(key), 2)
        messages.append(key + " : " + str(counts[key]) + "    " + error_message + "\n")

    return messages


def create_mail_title(span, condition):
    """time to messages


    Args:
        span (int): cache check span
        condition (str): server condition

    Returns:
        title (string): time and conditions to mail title


    """
    span_hour = str(int(span / 3600))
    return condition + " " + span_hour + "h"


def create_mail_body(messages):
    """status counts to messages


    Args:
        messages (list): messages

    Returns:
        body (string): statuses to mail body


    """
    body_message = messages[1:]
    body = "".join(body_message)

    return body


def create_mail(span):
    """create mail from caches which made in span


    Args:
        span (int): cache check span

    Returns:
        title (string): time and conditions to mail title
        body (string): statuses to mail body


    """
    cache_paths = create_filter_caches(span)

    if not cache_paths:
        title = create_mail_title(span, "***Bad***")
        body = "no cache available"
        return title, body

    statuses = create_cache_statuses(cache_paths)

    if not statuses:
        title = create_mail_title(span, "***Bad***")
        body = "may move cache"
        return title, body

    counts = create_count_statuses(statuses)

    messages = create_messages(counts)

    title = create_mail_title(span, messages[0])
    body = create_mail_body(messages)

    return title, body


def main():
    """main function


    Args:

    Returns:


    """
    # if no args, then exit
    if not sys.argv[1]:
        return

    span = int(sys.argv[1])

    title, body = create_mail(span)

    cmd = 'echo "' + body + '" | mail -s "' + title + '" ' + MAIL_ADDRESS
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
