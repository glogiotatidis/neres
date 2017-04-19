import config


LOGIN = 'https://login.newrelic.com/login'
MONITORS = ('https://synthetics.newrelic.com/'
            'accounts/{}/monitors.json'.format(config.ACCOUNT))
ACCOUNT = ('https://synthetics.newrelic.com/'
           'accounts/{}/info.json'.format(config.ACCOUNT))
MONITOR_JSON = ('https://synthetics.newrelic.com/'
                'accounts/{}/monitors/'.format(config.ACCOUNT) + '{}.json')
MONITOR = ('https://synthetics.newrelic.com/'
           'accounts/{}/monitors/'.format(config.ACCOUNT) + '{}')
NEW_MONITOR = ('https://synthetics.newrelic.com/'
               'accounts/{}/monitors/new'.format(config.ACCOUNT))
MONITOR_LOCATIONS = ('https://synthetics.newrelic.com/'
                     'accounts/{}/locations/list.json'.format(config.ACCOUNT))
