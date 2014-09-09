from flask.ext.rq import get_worker
import sys
from rq import Queue, Connection, Worker
from joystick.app import app

with Connection():
    qs = map(Queue, sys.argv[1:]) or [Queue()]

    w = Worker(qs)
    with app.app_context():
        w.work()
