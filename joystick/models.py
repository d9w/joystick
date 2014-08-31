from .app import app
from flask.ext.sqlalchemy import SQLAlchemy
from subprocess import call
import string
import random

db = SQLAlchemy(app)

# base class, abstract if possible
class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cmd = db.Column(db.String(255))
    log_file = db.Column(db.String(255))

    def __init__(self, **kwargs):
        super(Command, self).__init__(**kwargs)
        if not self.cmd:
            raise AttributeError('Command must be constructed with a cmd value')
        if not self.log_file:
            self.log_file = '%s/%s___%s.log' % (app.config.get('LOG_ROOT'),
                    ''.join([c for c in self.cmd if c.isalnum() or c in ('_','-')]).rstrip(),
                    ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10)),
                    )
        open(self.log_file, 'a').close()

    def __repr__(self):
        return '<{}_{}:{}>>{}>'.format(self.__class__.__name__, self.id, self.cmd, self.log_file)

    # return the last x lines of the log file
    def get_log_tail(self, x):
        with open(self.log_file, 'r') as log_file:
            lines = log_file.readlines()
            return ''.join(lines[max(len(lines)-x,0):])

    # returns the whole log
    def get_log(self):
        # returns the whole log
        with open(self.log_file, 'r') as log_file:
            return log_file.read()

# shells run the command as a new thread and open a socket for communication with the command
# commands like ['ssh user@host', 'ipmitool shell', 'bash']
class ShellCommand(Command):
    socket_file = db.Column(db.String(255))

# loops are commands that run with a regular interval
# usually for checking the state of something
# commands like ['ping -c 5 host', 'ipmitool chassis power status', 'uptime']
class LoopCommand(Command):
    start_date = db.Column(db.Float) # in seconds since epoch
    interval = db.Column(db.Float) # in seconds

# buttons run commands in a new thread and lock the button until the command returns
# commands like ['ssh user@host reboot now', 'ipmitool chassis power cycle', 'reboot now']
class ButtonCommand(Command):
    locked = db.Column(db.Boolean, default=False)

    # locks, runs, then unlocks the command
    def push(self):
        self.locked = True
        db.session.commit()
        with open(self.log_file, 'a') as log_file:
            print 'here'
            call(self.cmd, shell=True, stdout=log_file, stderr=log_file)
            print 'done'
        self.locked = False
        db.session.commit()
