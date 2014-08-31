from flask import Flask

app = Flask('joystick')
app.config.from_pyfile('config.py')
app.config.from_pyfile(app.config['PRODUCTION_ROOT'] + '/production.cfg')

from . import views
from . import models
