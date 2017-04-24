# -*- coding: utf-8 -*-
import re
import os

import json
import six
import requests
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
    response = session.get(urls.MONITOR_JSON.format(monitor))
    response.raise_for_status()
    headers = {
        'Referer': response.url,
    }

    response = session.delete(urls.MONITOR_JSON.format(monitor),
                              headers=headers)
    response.raise_for_status()


@requires_login
def get_locations():
    response = session.get(urls.MONITOR_LOCATIONS)
    response.raise_for_status()

    return response.json()


@requires_login
def get_monitor(monitor):
    response = session.get(urls.MONITOR_JSON.format(monitor))
    response.raise_for_status()

    return response.json()


@requires_login
def update_monitor(monitor, *args, **kwargs):
    data = get_monitor(monitor)
    for prop in ['name', 'uri', 'frequency', 'locations', 'slaThreshold']:
        value = kwargs.get(prop, None)
        if value:
            data[prop] = value

    for prop in ['emails', 'locations']:
        if kwargs.get('clear_{}'.format(prop)):
            data[prop] = []

        values = kwargs.get('add_{}'.format(prop))
        if values:
            if isinstance(values, six.string_types):
                values = [values]
            data[prop] = list(set(data[prop] + list(values)))

        values = kwargs.get('remove_{}'.format(prop))
        if values:
            if isinstance(values, six.string_types):
                prop = [values]
            data[prop] = list(set(data[prop]) - set(values))

    _construct_metadata(
        validation_string=kwargs.get('validation_string'),
        bypass_head_request=kwargs.get('bypass_head_request'),
        verify_ssl=kwargs.get('verify_ssl'),
        redirect_is_failure=kwargs.get('redirect_is_failure'),
        metadata=data['metadata'])

    headers = {
        'Referer': urls.MONITOR.format(monitor),
        'Content-Type': 'application/json;charset=utf-8',
    }

    url = urls.MONITOR_JSON.format(monitor)
    response = session.put(url, data=json.dumps(data), headers=headers)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        try:
            error = response.json()['error']
        except (ValueError, KeyError):
            error = 'Bad request'
        return (1, error, {})

    return (0, urls.MONITOR.format(response.json()['id']), response.json())


def _construct_metadata(validation_string=None, bypass_head_request=None,
                        verify_ssl=None, redirect_is_failure=None,
                        metadata=None):
    if metadata is None:
        metadata = {}

    if bypass_head_request is True:
        metadata['nr.synthetics.metadata.job.options.simple.bypass.head'] = True
    elif bypass_head_request is False:
        metadata.pop('nr.synthetics.metadata.job.options.simple.bypass.head', None)

    if validation_string:
        metadata['nr.synthetics.metadata.job.options.response-validation'] = validation_string
    elif validation_string is False:
        metadata.pop('nr.synthetics.metadata.job.options.response-validation', None)

    if verify_ssl is True:
        metadata['nr.synthetics.metadata.job.options.tlsValidation'] = True
        metadata['nr.synthetics.monitor.tls-validation'] = True
    elif verify_ssl is False:
        metadata.pop('nr.synthetics.metadata.job.options.tlsValidation', None)
        metadata.pop('nr.synthetics.monitor.tls-validation', None)

    if redirect_is_failure is True:
        metadata['nr.synthetics.metadata.job.options.redirectIsFailure'] = True
        metadata['nr.synthetics.metadata.job.options.simple.redirect.is.failure'] = True
    elif redirect_is_failure is False:
        metadata.pop('nr.synthetics.metadata.job.options.redirectIsFailure', None)
        metadata.pop('nr.synthetics.metadata.job.options.simple.redirect.is.failure', None)

    return metadata


@requires_login
def create_monitor(name, uri, frequency, locations, emails=[],
                   validation_string='', bypass_head_request=False,
                   verify_ssl=False, redirect_is_failure=False,
                   slaThreshold=7):
    if isinstance(locations, six.string_types):
        locations = [locations]

    if isinstance(emails, six.string_types):
        emails = [emails]

    if validation_string and not bypass_head_request:
        raise Exception('Response validation requires to bypass HEAD request.')

    response = session.get(urls.NEW_MONITOR)
    response.raise_for_status()
    headers = {
        'Referer': response.url,
        'Content-Type': 'application/json;charset=utf-8',
    }

    metadata = _construct_metadata(validation_string, bypass_head_request,
                                   verify_ssl, redirect_is_failure)
    data = {
        'accountId': config.ACCOUNT,
        'name': name,
        'type': 'SIMPLE',
        'frequency': frequency,
        'uri': uri,
        'status': 'ENABLED',
        'slaThreshold': slaThreshold,
        'locations': locations,
        'conditions': [],
        'metadata': metadata,
        'emails': emails,
    }
    data = json.dumps(data)
    response = session.post(urls.MONITORS, data=data, headers=headers)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        try:
            error = response.json()['error']
        except (ValueError, KeyError):
            error = 'Bad request'
        return (1, error, {})

    return (0, urls.MONITOR.format(response.json()['id']), response.json())
