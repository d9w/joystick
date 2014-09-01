from .app import app
from flask.ext.sqlalchemy import SQLAlchemy
from subprocess import call
import string
import random

db = SQLAlchemy(app)

# collection of different commands
class Console(db.Model):
    name = db.Column(db.String(255), primary_key=True)
    shells = db.relationship('ShellCommand', backref='console', lazy='select')
    loops = db.relationship('LoopCommand', backref='console', lazy='select')
    buttons = db.relationship('ButtonCommand', backref='console', lazy='select')

# base class, abstract if possible
class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cmd = db.Column(db.String(255))
    log_file = db.Column(db.String(255))
    console_name = db.Column(db.String(255), db.ForeignKey('console.name'))
    type = db.Column(db.String(50))

    __mapper_args__ = {
            'polymorphic_identity':'command',
            'polymorphic_on':type
    }

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
    __tablename__ = 'shells'
    __mapper_args__ = {'polymorphic_identity':'shell'}
    id = db.Column(db.Integer, db.ForeignKey('command.id'), primary_key=True)
    socket_file = db.Column(db.String(255))

# loops are commands that run with a regular interval
# usually for checking the state of something
# commands like ['ping -c 5 host', 'ipmitool chassis power status', 'uptime']
class LoopCommand(Command):
    __tablename__ = 'loops'
    __mapper_args__ = {'polymorphic_identity':'loop'}
    id = db.Column(db.Integer, db.ForeignKey('command.id'), primary_key=True)
    start_date = db.Column(db.Float) # in seconds since epoch
    interval = db.Column(db.Float) # in seconds

# buttons run commands in a new thread and lock the button until the command returns
# commands like ['ssh user@host reboot now', 'ipmitool chassis power cycle', 'reboot now']
class ButtonCommand(Command):
    __tablename__ = 'buttons'
    __mapper_args__ = {'polymorphic_identity':'button'}
    id = db.Column(db.Integer, db.ForeignKey('command.id'), primary_key=True)
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
