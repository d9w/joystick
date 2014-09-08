import time
from flask.ext.rq import job

@job
def test_job(test_data):
    print test_data
    print 'ran job'

@job
def serve_log(filename):
    """Example of how to send server generated events to clients."""
    while True:
        time.sleep(0.1)
        filename = '/prod/joystick/testlog'
        with open(filename,'r') as log_file:
            lines = log_file.readlines()
        socketio.emit('log', {'lines': ''.join(lines[max(len(lines)-5,0):])}, namespace='/test')
