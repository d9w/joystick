from flask import Flask
from flask.ext.testing import TestCase as Base, Twill
from flask.ext.sqlalchemy import SQLAlchemy

from joystick.extensions import db

class TestCase(Base):

    def create_app(self):

        app = Flask('joystick')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/joystick_test'
        db.init_app(app)
        return app

    def setUp(self):

        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()
