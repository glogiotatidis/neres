#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import humanize
from colorclass import Color, Windows
from terminaltables import SingleTable

import newrelic
from spinner import Spinner


@click.command()
@click.argument('monitor')
def get_monitor(monitor):
    with Spinner('Fetching monitor: '):
        monitor = newrelic.get_monitor(monitor)

    status = monitor['status'].lower()
    if status in ('muted', 'disabled'):
        status = Color(u'{autoyellow}❢{/autoyellow}')
    else:
        status = Color(u'{autogreen}✔{/autogreen}')

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
    table.title = Color('{autoblack}Monitor{/autoblack}')
    print(table.table)


@click.command()
@click.argument('monitor')
def delete_monitor(monitor):
    with Spinner('Deleting monitor {}: '.format(monitor), remove_message=False):
        newrelic.delete_monitor(monitor)
    print(Color(u'{autogreen}OK{/autogreen}'))


@click.command()
def list_locations():
    with Spinner('Fetching locations: '):
        locations = newrelic.get_locations()

    data = [[
        '#',
        'City',
        'Continent',
        'Code',
        'Availability',
        'Accessibility',
    ]]

    for number, location in enumerate(locations.values()):
        available = Color(u'{autogreen}✔{/autogreen}')
        if not location['available']:
            Color(u'{autored}✖{/autored}')

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
    table.title = Color('{autoblack}Locations{/autoblack}')

    for i in [0, 4, 5]:
        table.justify_columns[i] = 'right'

    print(table.table)


@click.command()
def list_monitors():
    with Spinner('Fetching monitors: '):
        monitors = newrelic.get_monitors()

    data = [[
        '#',
        'H',
        'S',
        'Name',
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
            health = Color(u'{autogreen}✔{/autogreen}')
        elif success_ratio > 0.95:
            health = Color(u'{autoyellow}❢{/autoyellow}')
        else:
            health = Color(u'{autored}✖{/autored}')
        monitor['health'] = health

        status = monitor['status'].lower()
        if status in ('muted', 'disabled'):
            status = Color(u'{autoyellow}❢{/autoyellow}')
        else:
            status = Color(u'{autogreen}✔{/autogreen}')
        monitor['status'] = status

    for number, monitor in enumerate(monitors, 1):

        data.append([
            number,
            monitor['health'],
            monitor['status'],
            monitor['name'],
            '{:.1f}%'.format(100 * monitor.get('success_ratio', 0)),
            humanize.naturalsize(monitor.get('avg_size', 0), binary=True),
            '{:.1f} ms'.format(monitor.get('load_time_50th_pr', 0)),
            '{:.1f} ms'.format(monitor.get('load_time_95th_pr', 0)),
            '{} min'.format(monitor['frequency']),
            len(monitor['locations']),
            len(monitor['emails'])
        ])

    table = SingleTable(data)
    table.title = Color('{autoblack}Monitors{/autoblack}')

    for i in [1, 2]:
        table.justify_columns[i] = 'center'

    for i in [0, 4, 5, 6, 7, 8, 9, 10]:
        table.justify_columns[i] = 'right'

    table.justify_columns[3] = 'left'

    print(table.table)


@click.group()
def main():
    newrelic.initialize_cookiejar()



main.add_command(list_monitors, name='list-monitors')
main.add_command(list_locations, name='list-locations')
main.add_command(delete_monitor, name='delete-monitor')
main.add_command(get_monitor, name='get-monitor')


if __name__ == "__main__":
    # Does nothing if not on Windows.
    Windows.enable(auto_colors=True, reset_atexit=True)
    main()
