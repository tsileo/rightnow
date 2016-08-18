# coding: utf-8
from flask_httpauth import HTTPBasicAuth

from config import CONFIG

auth = HTTPBasicAuth()

users = CONFIG.get('users', {})


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


