SYNTHETICS = 'https://synthetics.newrelic.com'
LOGIN = 'https://login.newrelic.com/login'
MONITORS = 'https://synthetics.newrelic.com/accounts/{account}/monitors.json'
MONITORS_V2 = ('https://synthetics.newrelic.com/accounts/{account}'
               '/v2/monitors.json?offset={offset}&limit=15')
ACCOUNT_INFO = 'https://synthetics.newrelic.com/accounts/{account}/info.json'
MONITOR_JSON = 'https://synthetics.newrelic.com/accounts/{account}/monitors/{monitor}.json'
MONITOR = 'https://synthetics.newrelic.com/accounts/{account}/monitors/{monitor}'
NEW_MONITOR = 'https://synthetics.newrelic.com/accounts/{account}/monitors/new'
MONITOR_LOCATIONS = 'https://synthetics.newrelic.com/accounts/{account}/locations/list.json'
IDLE = 'https://login.newrelic.com/idle_timeout'
MONITOR_STOPLIGHT = ('https://synthetics.newrelic.com/accounts/{account}'
                     '/monitors/{monitor}/stoplight.json')
