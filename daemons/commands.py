from flask.ext.rq import job

@job
def push_button(button_id):
    from joystick.app import app
    from joystick.models import Command, db
    from subprocess import Popen
    button = Command.query.get(button_id)
    with open(button.log_file, 'a') as log_file:
        process = Popen(button.cmd, shell=True, stdout=log_file, stderr=log_file)
    button.pid = process.pid
    db.session.add(button)
    db.session.commit()
