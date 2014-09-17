from .app import app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.rq import job
from daemons.commands import push_button, start_shell
from redis import Redis
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
import string
import random
import os
import signal

db = SQLAlchemy(app)
scheduler = Scheduler(connection=Redis())

# collection of different commands
class Console(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    shells = db.relationship('ShellCommand', backref='console', lazy='select')
    loops = db.relationship('LoopCommand', backref='console', lazy='select')
    buttons = db.relationship('ButtonCommand', backref='console', lazy='select')

# base class, abstract if possible
class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cmd = db.Column(db.String(255))
    log_file = db.Column(db.String(255))
    console_id = db.Column(db.Integer, db.ForeignKey('console.id'))
    type = db.Column(db.String(50))
    pid = db.Column(db.Integer, default=-1)

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
        return '<{}_{}:\'{} >> {}\'>'.format(self.__class__.__name__, self.id, self.cmd, self.log_file)

    def get_log_tail(self, x):
        with open(self.log_file, 'r') as log_file:
            lines = log_file.readlines()
            return ''.join(lines[max(len(lines)-x,0):])

    def get_log(self):
        with open(self.log_file, 'r') as log_file:
            return log_file.read()

    def stop(self):
        if self.is_running():
            os.kill(self.pid, signal.SIGKILL)

    def is_running(self):
        if self.pid > 0:
            try:
                os.kill(self.pid, 0)
            except OSError:
                return False
            return True
        return False

    def delete(self):
        self.stop()
        os.remove(self.log_file)

# shells run the command as a new thread and open a socket for communication with the command
# commands like ['ssh user@host', 'ipmitool shell', 'bash']
class ShellCommand(Command):
    __tablename__ = 'shells'
    __mapper_args__ = {'polymorphic_identity':'shell'}
    id = db.Column(db.Integer, db.ForeignKey('command.id'), primary_key=True)
    socket = db.Column(db.String(255))

    def __init__(self, **kwargs):
        super(ShellCommand, self).__init__(**kwargs)
        if not self.socket:
            self.socket = '%s/%s___%s.log' % (app.config.get('SOCKET_ROOT'),
                    ''.join([c for c in self.cmd if c.isalnum() or c in ('_','-')]).rstrip(),
                    ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10)),
                    )

    def start(self):
        start_shell.delay(self.id)

# loops are commands that run with a regular interval
# usually for checking the state of something
# commands like ['ping -c 5 host', 'ipmitool chassis power status', 'uptime']
class LoopCommand(Command):
    __tablename__ = 'loops'
    __mapper_args__ = {'polymorphic_identity':'loop'}
    id = db.Column(db.Integer, db.ForeignKey('command.id'), primary_key=True)
    start_date = db.Column(db.Float) # in seconds since epoch
    interval = db.Column(db.Float) # in seconds

    def start(self):
        scheduler.schedule(scheduled_time=datetime.utcfromtimestamp(0)+timedelta(seconds=self.start_date),
                func=push_button,
                args=[self.id],
                interval=self.interval,
                repeat=None)

    def is_scheduled(self):
        for job in scheduler.get_jobs():
            if job.func_name=='daemons.commands.push_button' and self.id in job.args:
                return True
        return False

    def stop(self):
        super(LoopCommand, self).stop()
        for job in scheduler.get_jobs():
            if job.func_name=='daemons.commands.push_button' and self.id in job.args:
                job.delete()

    def start_timestamp(self):
        return (datetime.utcfromtimestamp(0)+timedelta(seconds=self.start_date)).strftime('UTC %Y-%m-%d %H:%M:%S')

# buttons run commands in a new thread and lock the button until the command returns
# commands like ['ssh user@host reboot now', 'ipmitool chassis power cycle', 'reboot now']
class ButtonCommand(Command):
    __tablename__ = 'buttons'
    __mapper_args__ = {'polymorphic_identity':'button'}
    id = db.Column(db.Integer, db.ForeignKey('command.id'), primary_key=True)

    def push(self):
        if not self.is_running():
            push_button.delay(self.id)
