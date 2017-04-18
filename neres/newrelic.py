# -*- coding: utf-8 -*-
import re
import os
from six.moves.http_cookiejar import LWPCookieJar

import config
import urls
import session

session = session.Session()
session.cookies = LWPCookieJar(config.COOKIEJAR)


def initialize_cookiejar():
    if not os.path.exists(config.COOKIEJAR):
        session.cookies.save()
        os.chmod(config.COOKIEJAR, 0o600)
    else:
        session.cookies.load(ignore_discard=True)


def requires_login(fn):
    def wrapped(*args, **kwargs):
        if not check_if_logged_in():
            login()
        return fn(*args, **kwargs)
    return wrapped


def check_if_logged_in():
    response = session.get(urls.ACCOUNT, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 200:
        return True
    return False


def login():
    response = session.get(urls.LOGIN)
    response.raise_for_status()

    try:
        token = re.search('name="authenticity_token" value="(.+?)"',
                          response.content).groups()[0]
    except AttributeError:
        Exception("Can't get CSRF token to login.")

    payload = {
        'login[email]': config.EMAIL,
        'login[password]': config.PASSWORD,
        'login[remember_me]': '1',
        'return_to': 'https://rpm.newrelic.com/auth/newrelic',
        'utf8': '✓',
        'authenticity_token': token,
        'commit': 'Sign in'
    }
    response = session.post(urls.LOGIN, data=payload, add_xsrf_token=False)
    response.raise_for_status()
    if 'login_email' in response.content:
        raise Exception('Login Failed')
    session.cookies.save(ignore_discard=True)


@requires_login
def get_monitors():
    response = session.get(urls.MONITORS)
    response.raise_for_status()
    data = response.json()

    # sort data by name
    data = sorted(data, key=lambda x: x['name'])

    return data


@requires_login
def delete_monitor(monitor):
    response = session.get(urls.MONITOR.format(monitor))
    response.raise_for_status()
    headers = {
        'Referer': response.url,
    }

    response = session.delete(urls.MONITOR.format(monitor),
                              headers=headers)
    response.raise_for_status()


@requires_login
def get_monitor(monitor):
    response = session.get(urls.MONITOR.format(monitor))
    response.raise_for_status()

    return response.json()
