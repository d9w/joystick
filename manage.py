from flask.ext.script import Manager

from joystick.app import app
from joystick.extensions import db

manager = Manager(app)

@manager.command
def run():
    app.run()

@manager.command
def initdb():

    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    manager.run()
