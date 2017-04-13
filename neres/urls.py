import config


LOGIN = 'https://login.newrelic.com/login'
MONITORS = ('https://synthetics.newrelic.com/'
            'accounts/{}/monitors.json'.format(config.ACCOUNT))
ACCOUNT = ('https://synthetics.newrelic.com/'
           'accounts/{}/info.json'.format(config.ACCOUNT))
MONITOR = ('https://synthetics.newrelic.com/'
           'accounts/{}/monitors/'.format(config.ACCOUNT) + '{}.json')
