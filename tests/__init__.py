from flask import Flask
from flask.ext.testing import TestCase as Base
from flask.ext.sqlalchemy import SQLAlchemy

from joystick.app import app as APP
from joystick.models import db

import os
from shutil import rmtree

class TestCase(Base):

    def create_app(self):

        app = APP
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_ECHO'] = False
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/joystick_test'
        #app.config['PRODUCTION_ROOT'] = '/prod/joystick_test'
        #app.config['LOG_ROOT'] = app.config['PRODUCTION_ROOT'] + '/logs'
        self.LOG_ROOT = app.config['LOG_ROOT']
        db.init_app(app)
        return app

    def setUp(self):

        if os.path.exists(self.LOG_ROOT):
            rmtree(self.LOG_ROOT, ignore_errors=True)
        os.makedirs(self.LOG_ROOT)
        db.create_all()

    def tearDown(self):

        rmtree(self.LOG_ROOT, ignore_errors=True)
        db.session.remove()
        db.drop_all()
