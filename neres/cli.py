#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import os
import platform
import subprocess
from datetime import datetime

import click
import humanize
import yaml
import yamlordereddictloader
from terminaltables import SingleTable

import neres.newrelic as newrelic
import neres.urls as urls
from .spinner import Spinner


@click.command(help='Add a new monitor')
@click.argument('name')
@click.argument('uri')
@click.option('--location', default=['AWS_US_WEST_1'], multiple=True,
              help='Monitor locations. Defaults to AWS_US_WEST_1. Get a list of available monitor'
                   'locations with `list-locations`. Repeat for multiple locations.')
@click.option('--frequency', default='10',
              type=click.Choice(['1', '5', '10', '15', '30', '60', '360', '720', '1440']),
              callback=lambda x, y, z: int(z),
              help='Monitor frequency. Defaults to 10 minutes')
@click.option('--email', default=[], multiple=True,
              help='Send alerts to email. Repeat for multiple alerts.')
@click.option('--validation-string', default='',
              help='Add a validation string to look for in the response (optional)')
@click.option('--bypass-head-request', default=False, is_flag=True,
              help=('Send full HTTP GET requests. '
                    'Will be automatically set if validation-string is provided.'))
@click.option('--verify-ssl', default=False, is_flag=True,
              help='Run a detailed OpenSSL handshake and alert if it fails.')
@click.option('--redirect-is-failure', default=False, is_flag=True,
              help='HTTP redirect codes result in a failure')
@click.option('--sla-threshold', default=7, type=int,
              help='Set Apdex Threshold. Defaults to 7 seconds.')
@click.option('--raw', default=False, is_flag=True, help='Return raw json response')
@click.pass_context
def add_monitor(ctx, name, uri, location, frequency, email, validation_string,
                bypass_head_request, verify_ssl, redirect_is_failure, sla_threshold, raw):
    if validation_string:
        # We must bypass head request we're to validate string.
        bypass_head_request = True

    with Spinner('Creating monitor: ', remove_message=raw):
        status, message, monitor = newrelic.create_monitor(
            ctx.obj['ACCOUNT'], name, uri, frequency, location, email,
            validation_string, bypass_head_request, verify_ssl, redirect_is_failure,
            sla_threshold)

    if raw:
        print(json.dumps(monitor))
        return

    if status == 0:
        print(click.style(u'OK', fg='green', bold=True))
        print('Monitor: ' + message)
    else:
        print(click.style(u'Error', fg='red', bold=True))
        raise click.ClickException(message)


@click.command(help='Update an existing monitor')
@click.argument('monitor')
@click.option('--name', default=None, help='Change the name of the monitor')
@click.option('--uri', default=None, help='Change the URI to monitor')
@click.option('--add-location', 'add_locations', default=None, multiple=True,
              help=('Add a monitor location. Repeat for multiple locations. '
                    'Get available locations with `list-locations`'))
@click.option('--clear-locations', default=False, is_flag=True,
              help='Remove all monitor locations. Must be combined with `add-location`')
@click.option('--remove-location', 'remove_locations', default=None, multiple=True,
              help='Remove a monitor location. Repeats for multiple locations')
@click.option('--add-email', 'add_emails', default=None, multiple=True,
              help='Add an email to receive alerts. Repeat for multiple emails')
@click.option('--remove-email', 'remove_emails', default=None, multiple=True,
              help='Remove email from alert list. Repeat for multiple emails')
@click.option('--clear-emails', default=False, is_flag=True,
              help='Remove all emails from alert list')
@click.option('--frequency', default=None,
              type=click.Choice(['1', '5', '10', '15', '30', '60', '360', '720', '1440']),
              help='Change monitor frequency.')
@click.option('--sla-threshold', 'slaThreshold', default=None,
              help='Change Apdex Threshold')
@click.option('--validation-string', default=None, help='Set or change the validation string')
@click.option('--no-validation-string', default=None, is_flag=True,
              help='Remove validation string check')
@click.option('--bypass-head-request/--no-bypass-head-request', default=None, is_flag=True,
              help='Set / unset sending of full HTTP GET requests')
@click.option('--verify-ssl/--no-verify-ssl', default=None, is_flag=True,
              help='Set / unset OpenSSL verification')
@click.option('--redirect-is-failure/--no-redirect-is-failure', default=None, is_flag=True,
              help='Set / unset redirect is failure check')
@click.option('--status',
              type=click.Choice(['enabled', 'disabled', 'muted', 'ENABLED', 'DISABLED', 'MUTED']),
              default=None, help='Set monitor status',
              callback=lambda x, y, z: z.upper() if z else None)  # Yes this is horrible.
@click.option('--raw', default=False, is_flag=True, help='Return raw json response')
@click.pass_context
def update_monitor(ctx, monitor, **kwargs):
    if kwargs['no_validation_string']:
        if kwargs['validation_string']:
            raise click.ClickException(
                'Flags --validation-string and --no-validation-string cannot be combined')

        kwargs['validation_string'] = False

    if kwargs['validation_string']:
        # We must bypass head request we're to validate string.
        kwargs['bypass_head_request'] = True

    if kwargs['clear_locations'] and not kwargs['add_locations']:
        raise click.ClickException(
            'You need at least one location. Combine --clear-locations'
            'with --add-location.')

    with Spinner('Updating monitor: ', remove_message=kwargs['raw']):
        status, message, monitor = newrelic.update_monitor(ctx.obj['ACCOUNT'], monitor, **kwargs)

    if kwargs['raw']:
        print(json.dumps(monitor))
        return

    if status == 0:
        print(click.style(u'OK', fg='green', bold=True))
        print('Monitor: ' + message)
    else:
        print(click.style(u'Error', fg='red', bold=True))
        raise click.ClickException(message)


@click.command(help='Get information for a monitor')
@click.argument('monitor')
@click.option('--raw', default=False, is_flag=True, help='Return raw json response')
@click.pass_context
def get_monitor(ctx, monitor, raw):
    with Spinner('Fetching monitor: '):
        monitor = newrelic.get_monitor(ctx.obj['ACCOUNT'], monitor)

    if raw:
        print(json.dumps(monitor))
        return

    severity = monitor.get('severity', 0)
    if severity == 2:
        health = click.style(u'✔', fg='green')
    elif severity == 1:
        health = click.style(u'❢', fg='yellow')
    else:
        health = click.style(u'✖', fg='red')
    monitor['health'] = health

    status = monitor['status'].lower()
    if status in ('muted', 'disabled'):
        status = click.style(u'❢ {}'.format(status), fg='yellow')
    else:
        status = click.style(u'✔ OK', fg='green')

    data = [
        ['Monitor', monitor['id']],
        ['Status', status],
        ['Health', health],
        ['Name', monitor['name']],
        ['URI', monitor['uri']],
        ['Type', monitor['type']],
        ['Locations', ', '.join(monitor['locations'])],
        ['slaThreshold', monitor['slaThreshold']],
        ['Emails', ', '.join(monitor['emails'])],
        ['Frequency', monitor['frequency']],
        ['Created', monitor['createdAt']],
        ['Modified', monitor['modifiedAt']],

    ]

    table = SingleTable(data)
    table.title = click.style('Monitor', fg='black')
    print(table.table)


@click.command(help='Delete a monitor')
@click.argument('monitor')
@click.option('--confirm', default=None, help='Skip confirmation prompt by supplying monitor id')
@click.pass_context
def delete_monitor(ctx, monitor, confirm):
    if not confirm:
        confirm = click.prompt('''
 ! WARNING: Destructive Action
 ! This command will destroy the monitor: {monitor}
 ! To proceed, type "{monitor}" or
   re-run this command with --confirm={monitor}

'''.format(monitor=monitor), prompt_suffix='> ')
    if confirm.strip() != monitor:
        print('abort')
        sys.exit(1)

    with Spinner('Deleting monitor {}: '.format(monitor), remove_message=False):
        newrelic.delete_monitor(ctx.obj['ACCOUNT'], monitor)
    print(click.style(u'OK', fg='green', bold=True))


@click.command(help='List available monitor locations')
@click.option('--raw', default=False, is_flag=True, help='Return raw json response')
@click.pass_context
def list_locations(ctx, raw):
    with Spinner('Fetching locations: '):
        locations = newrelic.get_locations(ctx.obj['ACCOUNT'])

    if raw:
        print(json.dumps(locations))
        return

    data = [[
        '#',
        'City',
        'Continent',
        'Code',
        'Availability',
        'Accessibility',
    ]]

    for number, location in enumerate(locations.values()):
        available = click.style(u'✔', fg='green')
        if not location['available']:
            click.style(u'✖', fg='red')

        private = 'Private' if location['private'] else 'Public'

        data.append([
            number,
            location['label'],
            location['continent'],
            location['name'],
            available,
            private,
        ])

    table = SingleTable(data)
    table.title = click.style('Locations', fg='black')

    for i in [0, 4, 5]:
        table.justify_columns[i] = 'right'

    print(table.table)


@click.command(help='List monitors')
@click.option('--ids-only', default=False, is_flag=True, help='List monitor IDs only')
@click.option('--raw', default=False, is_flag=True, help='Return raw json response')
@click.pass_context
def list_monitors(ctx, ids_only, raw):
    with Spinner('Fetching monitors: '):
        monitors = newrelic.get_monitors(ctx.obj['ACCOUNT'])

    if raw:
        print(json.dumps(monitors))
        return

    if ids_only:
        for monitor in monitors:
            print(monitor['id'])
        return

    data = [[
        '#',
        'H',
        'S',
        'Name',
        'ID',
        'Success\nRate',
        'Avg Size',
        'Load time\n(50th PR)',
        'Load time\n(95th PR)',
        'Frequency',
        'Loca\ntions',
        'Notif\nEmails',
    ]]

    for monitor in monitors:
        severity = monitor.get('severity', 0)
        if severity == 2:
            health = click.style(u'✔', fg='green')
        elif severity == 1:
            health = click.style(u'❢', fg='yellow')
        else:
            health = click.style(u'✖', fg='red')
        monitor['health'] = health

        status = monitor['status'].lower()
        if status in ('muted', 'disabled'):
            status = click.style(u'❢', fg='yellow')
        else:
            status = click.style(u'✔', fg='green')
        monitor['status'] = status

    for number, monitor in enumerate(monitors, 1):

        data.append([
            number,
            monitor['health'],
            monitor['status'],
            monitor['name'],
            monitor['id'],
            '{:.1f}%'.format(100 * monitor.get('success_ratio', 0)),
            humanize.naturalsize(monitor.get('avg_size', 0), binary=True),
            '{:.1f} ms'.format(monitor.get('load_time_50th_pr', 0)),
            '{:.1f} ms'.format(monitor.get('load_time_95th_pr', 0)),
            '{} min'.format(monitor['frequency']),
            len(monitor['locations']),
            len(monitor['emails'])
        ])

    table = SingleTable(data)
    table.title = click.style('Monitors', fg='black')

    for i in [1, 2]:
        table.justify_columns[i] = 'center'

    for i in [0, 5, 6, 7, 8, 9, 10, 11]:
        table.justify_columns[i] = 'right'

    table.justify_columns[3] = 'left'

    print(table.table)


@click.command(help='Open monitor in Web browser')
@click.argument('monitor')
@click.pass_context
def open_monitor(ctx, monitor):
    url = urls.MONITOR.format(account=ctx.obj['ACCOUNT'], monitor=monitor)
    if platform.system() == 'Windows':
        os.startfile(url)
    elif platform.system() == 'Darwin':
        subprocess.Popen(['open', url])
    else:
        subprocess.Popen(['xdg-open', url])


@click.command(help='List accounts')
@click.option('--raw', is_flag=True, default=False, help='Return raw json response')
def list_accounts(raw):
    with Spinner('Fetching accounts: '):
        accounts = newrelic.get_accounts()

    if raw:
        for account in accounts:
            print(account[0])

    data = [[
        'ID',
        'Name'
    ]]
    for account in accounts:
        data.append([account['id'], account['name']])

    table = SingleTable(data)
    table.title = click.style('Accounts', fg='black')
    print(table.table)


@click.command(help='Login to newrelic')
@click.pass_context
def login(ctx):
    email = ctx.obj['EMAIL']
    if not email:
        email = click.prompt('Email')

    password = ctx.obj['PASSWORD']
    if not password:
        password = click.prompt('Password', hide_input=True)

    with Spinner('Logging in: ', remove_message=False):
        newrelic.login(email, password)
    print(click.style(u'OK', fg='green', bold=True))


@click.command(help='Update from state')
@click.argument('statefile', type=click.File('rb'))
@click.option('--apply', default=False, is_flag=True)
@click.pass_context
def update_from_statefile(ctx, apply, statefile):
    if not apply:
        print('This is a dry run. Run with --apply to make the changes.\n')

    with Spinner('Getting current state: '):
        there_data = newrelic.get_state(ctx.obj['ACCOUNT'])
    here_data = yaml.load(statefile)

    changes = 0
    for monitor in here_data:
        for there_monitor in there_data:
            if there_monitor['id'] == monitor['id']:
                break
        else:
            print('Monitor {} only exists in statefile, skipping.'.format(monitor['id']))
            continue

        if there_monitor != monitor:
            monitor_id = monitor.pop('id')
            with Spinner('Updating monitor {}: '.format(monitor_id), remove_message=False):
                if apply:
                    status, message, _ = newrelic.update_monitor(ctx.obj['ACCOUNT'],
                                                                 monitor_id,
                                                                 **monitor)
                    if status == 0:
                        print(click.style(u'OK', fg='green', bold=True))
                    else:
                        print(click.style(u'Error', fg='red', bold=True))
                        raise click.ClickException(message)
            changes += 1

    if changes == 0:
        print('No changes made.')
    else:
        print('Successfully updated {} monitors'.format(changes))


@click.command(help='Get state')
@click.pass_context
def get_state(ctx, return_data=False):
    with Spinner('Fetching state: '):
        state = newrelic.get_state(ctx.obj['ACCOUNT'])

    print('# Generated on {}'.format(datetime.utcnow().isoformat()))
    print(yaml.dump(
        state,
        allow_unicode=True,
        default_flow_style=False,
        Dumper=yamlordereddictloader.SafeDumper,
    ))


@click.group()
@click.option('--email', help='New Relic login email')
@click.option('--password', help='New Relic login password')
@click.option('--account', help=('New Relic account to work on. You can get a list of accounts '
                                 'with `list-accounts`. Defaults to first listed account'))
@click.option('--environment', default='newrelic',
              help=('Default `newrelic`. Define different environments for '
                    'different New Relic accounts.'))
@click.pass_context
def cli(ctx, email, password, account, environment):
    cookiejar = os.path.expanduser('~/.config/neres/{}.cookies'.format(environment))
    if not os.path.exists(os.path.dirname(cookiejar)):
        os.makedirs(os.path.dirname(cookiejar), 0o700)
    newrelic.initialize_cookiejar(cookiejar)

    if ctx.invoked_subcommand != 'login':
        with Spinner('Authorizing: '):
            if all([email, password]):
                newrelic.login(email, password)
            else:
                if not newrelic.check_if_logged_in():
                    raise click.ClickException('Login first')

        if not account and ctx.invoked_subcommand != 'list-accounts':
            account = newrelic.get_accounts()[0]['id']

    ctx.obj = {}
    ctx.obj['ACCOUNT'] = account
    ctx.obj['EMAIL'] = email
    ctx.obj['PASSWORD'] = password


cli.add_command(list_monitors, name='list-monitors')
cli.add_command(list_locations, name='list-locations')
cli.add_command(delete_monitor, name='delete-monitor')
cli.add_command(get_monitor, name='get-monitor')
cli.add_command(add_monitor, name='add-monitor')
cli.add_command(update_monitor, name='update-monitor')
cli.add_command(list_accounts, name='list-accounts')
cli.add_command(open_monitor, name='open')
cli.add_command(login, name='login')
cli.add_command(get_state, name='get-state')
cli.add_command(update_from_statefile, name='update-from-statefile')


if __name__ == '__main__':
    cli(auto_envvar_prefix='NERES')
