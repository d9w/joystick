import os

PROJECT = 'joystick'
PRODUCTION_ROOT = '/etc/joystick'

DEBUG = True
TESTING = False

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

SECRET_KEY = '' # override in production

SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/joystick'

# Flask-cache
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 60

# Flask-OAuth for Google
BASE_URL = 'https://www.google.com/accounts/'
AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
REQUEST_TOKEN_URL = None
REQUEST_TOKEN_PARAMS = {'scope': 'https://www.googleapis.com/auth/userinfo.email', 'response_type': 'code'}
ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
ACCESS_TOKEN_METHOD = 'POST'
ACCESS_TOKEN_PARAMS = {'grant_type': 'authorization_code'}
CONSUMER_KEY = '' # override in production
CONSUMER_SECRET = '' # override in production

# Flask-mail
MAIL_DEBUG = DEBUG
MAIL_SERVER = '' # override in production
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = '' # override in production
MAIL_PASSWORD = '' # override in production
MAIL_DEFAULT_SENDER = MAIL_USERNAME
