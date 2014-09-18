from flask.ext.script import Manager, Shell
from flask.ext.rq import get_worker
from gevent import monkey
from shutil import rmtree
from datetime import datetime
import os

from joystick.app import app
from joystick.models import Console, ShellCommand, LoopCommand, ButtonCommand, db
from joystick.sockets import socketio

manager = Manager(app)

def init_data():
    console = Console(name='test')
    shell = ShellCommand(cmd='ssh root@infinilab.infinidat.com', console=console)
    shell = ShellCommand(cmd='zsh', console=console)
    loop = LoopCommand(cmd='date', console=console,
            start_date=(datetime.utcnow()-datetime.utcfromtimestamp(0)).total_seconds(),
            interval=10.0)
    button = ButtonCommand(cmd='ping www.google.com', console=console)
    button2 = ButtonCommand(cmd='traceroute www.google.com', console=console)
    db.session.add_all([console, shell, loop, button, button2])
    db.session.commit()

@manager.command
def initdb():

    db.drop_all()
    log_root = app.config['LOG_ROOT']
    if os.path.exists(log_root):
        rmtree(log_root, ignore_errors=True)
    os.makedirs(log_root)
    db.create_all()
    init_data()

@manager.command
def run():
    monkey.patch_all()
    socketio.run(app)

@manager.shell
def _make_context():
    return dict(app=app, db=db)

if __name__ == '__main__':
    manager.run()
