import os

from decouple import config


ACCOUNT = config('NERES_ACCOUNT')
EMAIL = config('NERES_EMAIL')
PASSWORD = config('NERES_PASSWORD')
ENVIRONMENT = config('NERES_ENVIRONMENT', default='newrelic')

cookiejar = os.path.expanduser('~/.config/neres/{}.cookies'.format(ENVIRONMENT))
if not os.path.exists(os.path.dirname(cookiejar)):
    os.makedirs(os.path.dirname(cookiejar), 0o700)
COOKIEJAR = config('NERES_COOKIEJAR', default=cookiejar)
