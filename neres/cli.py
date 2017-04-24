#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import platform
import subprocess


import click
import humanize
from terminaltables import SingleTable

import newrelic
import urls
from spinner import Spinner


@click.command()
@click.argument('name')
@click.argument('uri')
@click.option('--location', default=['AWS_US_WEST_1'], multiple=True)
@click.option('--frequency', default=10)
@click.option('--email', default=[''], multiple=True)
@click.option('--validation-string', default='')
@click.option('--bypass-head-request', default=False, is_flag=True)
@click.option('--verify-ssl', default=False, is_flag=True)
@click.option('--redirect-is-failure', default=False, is_flag=True)
@click.option('--sla-threshold', default=7)
@click.option('--raw', default=False, is_flag=True)
def add_monitor(name, uri, location, frequency, email, validation_string,
                bypass_head_request, verify_ssl, redirect_is_failure, sla_threshold, raw):
    if validation_string:
        # We must bypass head request we're to validate string.
        bypass_head_request = True

    with Spinner('Creating monitor: ', remove_message=raw):
        status, message, monitor = newrelic.create_monitor(name, uri, frequency, location, email,
                                                           validation_string, bypass_head_request,
                                                           verify_ssl, redirect_is_failure,
                                                           sla_threshold)

    if raw:
        print(monitor)
        return

    if status == 0:
        print(click.style(u'OK', fg='green', bold=True))
        print('Monitor: ' + message)
    else:
        print(click.style(u'Error', fg='red', bold=True))
        raise click.ClickException(message)


@click.command()
@click.argument('monitor')
@click.option('--name', default=None)
@click.option('--uri', default=None)
@click.option('--add-location', 'add_locations', default=None, multiple=True)
@click.option('--clear-locations', default=False, is_flag=True)
@click.option('--remove-location', 'remove_locations', default=None, multiple=True)
@click.option('--add-email', 'add_emails', default=None, multiple=True)
@click.option('--remove-email', 'remove_emails', default=None, multiple=True)
@click.option('--clear-emails', default=False, is_flag=True)
@click.option('--frequency', default=None)
@click.option('--sla-threshold', 'slaThreshold', default=None)
@click.option('--validation-string', default=None)
@click.option('--no-validation-string', default=None, is_flag=True)
@click.option('--bypass-head-request/--no-bypass-head-request', default=None, is_flag=True)
@click.option('--verify-ssl/--no-verify-ssl', default=None, is_flag=True)
@click.option('--redirect-is-failure/--no-redirect-is-failure', default=None, is_flag=True)
@click.option('--raw', default=False, is_flag=True)
def update_monitor(monitor, **kwargs):
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
        status, message, monitor = newrelic.update_monitor(monitor, **kwargs)

    if kwargs['raw']:
        print(monitor)
        return

    if status == 0:
        print(click.style(u'OK', fg='green', bold=True))
        print('Monitor: ' + message)
    else:
        print(click.style(u'Error', fg='red', bold=True))
        raise click.ClickException(message)


@click.command()
@click.argument('monitor')
@click.option('--raw', default=False, is_flag=True)
def get_monitor(monitor, raw):
    with Spinner('Fetching monitor: '):
        monitor = newrelic.get_monitor(monitor)

    if raw:
        print(monitor)
        return

    status = monitor['status'].lower()
    if status in ('muted', 'disabled'):
        status = click.style(u'❢', fg='yellow')
    else:
        status = click.style(u'✔', fg='green')

    data = [
        ['Monitor', monitor['id']],
        ['Status', status],
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


@click.command()
@click.argument('monitor')
@click.option('--confirm', default=None)
def delete_monitor(monitor, confirm):
    if not confirm:
        confirm = click.prompt('''
 ! WARNING: Destructive Action
 ! This command will destroy the monitor:\n\t{monitor}
 ! To proceed, type "{monitor}" or
   re-run this command with --confirm={monitor}

'''.format(monitor=monitor), prompt_suffix='> ')
    if confirm.strip() != monitor:
        print('abort')
        sys.exit(1)

    with Spinner('Deleting monitor {}: '.format(monitor), remove_message=False):
        newrelic.delete_monitor(monitor)
    print(click.style(u'OK', fg='green', bold=True))


@click.command()
@click.option('--raw', default=False, is_flag=True)
def list_locations(raw):
    with Spinner('Fetching locations: '):
        locations = newrelic.get_locations()

    if raw:
        print(locations)
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


@click.command()
@click.option('--ids-only', default=False, is_flag=True)
@click.option('--raw', default=False, is_flag=True)
def list_monitors(ids_only, raw):
    with Spinner('Fetching monitors: '):
        monitors = newrelic.get_monitors()

    if raw:
        print(monitors)
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
        success_ratio = monitor.get('success_ratio', 0)
        if success_ratio == 1.0:
            health = click.style(u'✔', fg='green')
        elif success_ratio > 0.95:
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


@click.command()
@click.argument('monitor')
def open_monitor(monitor):
    url = urls.MONITOR.format(monitor)
    if platform.system() == 'Windows':
        os.startfile(url)
    elif platform.system() == 'Darwin':
        subprocess.Popen(['open', url])
    else:
        subprocess.Popen(['xdg-open', url])


@click.group()
def main():
    newrelic.initialize_cookiejar()


main.add_command(list_monitors, name='list-monitors')
main.add_command(list_locations, name='list-locations')
main.add_command(delete_monitor, name='delete-monitor')
main.add_command(get_monitor, name='get-monitor')
main.add_command(add_monitor, name='add-monitor')
main.add_command(update_monitor, name='update-monitor')
main.add_command(open_monitor, name='open')


if __name__ == "__main__":
    # Does nothing if not on Windows.
    main()
