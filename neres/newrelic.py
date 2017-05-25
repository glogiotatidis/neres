# -*- coding: utf-8 -*-
import re
import os
from collections import OrderedDict

import json
import six
import requests
from six.moves.http_cookiejar import LWPCookieJar

import neres.urls as urls
import neres.session as session

session = session.Session()


def initialize_cookiejar(cookiejar):
    session.cookies = LWPCookieJar(cookiejar)
    if not os.path.exists(cookiejar):
        session.cookies.save()
        os.chmod(cookiejar, 0o600)
    else:
        session.cookies.load(ignore_discard=True)


def check_if_logged_in():
    response = session.get(urls.IDLE, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 200:
        return True
    return False


def login(email, password):
    session.cookies.clear()
    response = session.get(urls.LOGIN)
    response.raise_for_status()

    try:
        token = re.search(b'name="authenticity_token" value="(.+?)"',
                          response.content).groups()[0]
    except AttributeError:
        Exception("Can't get CSRF token to login.")

    payload = {
        'login[email]': email,
        'login[password]': password,
        'login[remember_me]': '1',
        'return_to': 'https://rpm.newrelic.com/auth/newrelic',
        'utf8': '✓',
        'authenticity_token': token,
        'commit': 'Sign in'
    }
    response = session.post(urls.LOGIN, data=payload, add_xsrf_token=False)
    response.raise_for_status()
    if b'login_email' in response.content:
        raise Exception('Login Failed')
    session.cookies.save(ignore_discard=True)


def get_monitors(account):
    url = urls.MONITORS.format(account=account)
    response = session.get(url)
    response.raise_for_status()
    data = response.json()

    # sort data by name
    data = sorted(data, key=lambda x: x['name'])

    return data


def delete_monitor(account, monitor):
    url = urls.MONITOR_JSON.format(account=account, monitor=monitor)
    response = session.get(url)
    response.raise_for_status()
    headers = {
        'Referer': response.url,
    }

    url = urls.MONITOR_JSON.format(account=account, monitor=monitor)
    response = session.delete(url, headers=headers)
    response.raise_for_status()


def get_locations(account):
    url = urls.MONITOR_LOCATIONS.format(account=account)
    response = session.get(url)
    response.raise_for_status()

    return response.json()


def get_monitor(account, monitor):
    url = urls.MONITOR_JSON.format(account=account, monitor=monitor)
    response = session.get(url)
    response.raise_for_status()

    return response.json()


def update_monitor(account, monitor, *args, **kwargs):
    data = get_monitor(account, monitor)
    data['id'] = monitor
    data.pop('createdAt', None)
    data.pop('modifiedAt', None)

    data['currentChecks'] = 43200 / data['frequency']
    data['slaThreshold'] = int(data['slaThreshold'])

    for prop in ['name', 'uri', 'frequency',
                 'emails', 'locations', 'slaThreshold', 'status']:
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
        'Referer': urls.MONITOR.format(account=account, monitor=monitor),
        'Content-Type': 'application/json;charset=utf-8',
    }

    url = urls.MONITOR_JSON.format(account=account, monitor=monitor)
    response = session.put(url, data=json.dumps(data), headers=headers)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        try:
            error = response.json()['error']
        except (ValueError, KeyError):
            error = 'Bad request'
        return (1, error, {})

    url = urls.MONITOR.format(account=account, monitor=response.json()['id'])
    return (0, url, response.json())


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


def create_monitor(account, name, uri, frequency, locations, emails=[],
                   validation_string='', bypass_head_request=False,
                   verify_ssl=False, redirect_is_failure=False,
                   slaThreshold=7):
    if isinstance(locations, six.string_types):
        locations = [locations]

    if isinstance(emails, six.string_types):
        emails = [emails]

    if validation_string and not bypass_head_request:
        raise Exception('Response validation requires to bypass HEAD request.')

    response = session.get(urls.NEW_MONITOR.format(account=account))
    response.raise_for_status()
    headers = {
        'Referer': response.url,
        'Content-Type': 'application/json;charset=utf-8',
    }

    metadata = _construct_metadata(validation_string, bypass_head_request,
                                   verify_ssl, redirect_is_failure)
    data = {
        'accountId': account,
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
    url = urls.MONITORS.format(account=account)
    response = session.post(url, data=data, headers=headers)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        try:
            error = response.json()['error']
        except (ValueError, KeyError):
            error = 'Bad request'
        return (1, error, {})

    url = urls.MONITOR.format(account=account, monitor=response.json()['id'])
    return (0, url, response.json())


def get_accounts():
    response = session.get(urls.SYNTHETICS)
    response.raise_for_status()

    accountId = re.search(b'"accountId":(\d+)', response.content).groups()[0]

    response = session.get(urls.ACCOUNT_INFO.format(account=accountId.decode('utf-8')))
    response.raise_for_status()

    return response.json().get('accountList')


def get_state(account):
    data = []
    monitors = get_monitors(account)

    for monitor in monitors:
        monitor_details = get_monitor(account, monitor['id'])

        monitor_data = OrderedDict([
            ('id', monitor['id']),
            ('name', monitor_details['name']),
            ('status', monitor_details['status']),
            ('uri', monitor_details['uri']),
            ('slaThreshold', monitor_details['slaThreshold']),
            ('emails', monitor_details['emails'] or ''),
            ('locations', monitor_details['locations'] or ''),
            ('frequency', monitor_details['frequency']),
            ('verify_ssl', False),
            ('validation_string', False),
            ('bypass_head_request', False),
            ('redirect_is_failure', False),
        ])

        if monitor_details['metadata']:
            m = monitor_details['metadata']

            if m.get('nr.synthetics.metadata.job.options.simple.bypass.head') == 'true':
                monitor_data['bypass_head_request'] = True

            response_validation = m.get(
                'nr.synthetics.metadata.job.options.response-validation', False)
            monitor_data['validation_string'] = response_validation

            if m.get('nr.synthetics.monitor.tls-validation'):
                monitor_data['verify_ssl'] = True

            if m.get('nr.synthetics.metadata.job.options.simple.redirect.is.failure'):
                monitor_data['redirect_is_failure'] = True
        data.append(monitor_data)

    return data
