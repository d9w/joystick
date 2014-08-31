from flask.ext.script import Manager, Shell

from joystick.app import app
from joystick.models import db

manager = Manager(app)

@manager.command
def run():
    app.run()

@manager.command
def initdb():

    db.drop_all()
    db.create_all()

@manager.shell
def _make_context():
    return dict(app=app, db=db)

if __name__ == '__main__':
    manager.run()
