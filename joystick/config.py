import os

PROJECT = 'joystick'
PRODUCTION_ROOT = '/prod/joystick'
LOG_ROOT = PRODUCTION_ROOT + '/logs'
SOCKET_ROOT = PRODUCTION_ROOT + '/sockets'

DEBUG = True
TESTING = False

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

SECRET_KEY = '' # override in production

SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/joystick'

RQ_DEFAULT_HOST = 'localhost'
RQ_DEFAULT_PORT = 6379
