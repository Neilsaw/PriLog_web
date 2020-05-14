# -*- coding: utf-8 -*-
"""create token prilog rest api

     * create token




"""
import os
import secrets
import datetime
import json
import urllib.parse

token_dir = "token/"
if not os.path.exists(token_dir):
    os.mkdir(token_dir)


def create_token():
    """create token

    create token as json file

    with information : create date
                     : user name
                     : user purpose

    Args:

    Returns:


    """
    token = secrets.token_urlsafe()
    create_time = datetime.datetime.now()
    input_name = input("name >> ")
    input_purpose = input("purpose >> ")

    json.dump([token, str(create_time), str(input_name), str(input_purpose)],
              open(token_dir + urllib.parse.quote(token) + '.json', 'w'))

    print(token)


if __name__ == "__main__":
    create_token()
