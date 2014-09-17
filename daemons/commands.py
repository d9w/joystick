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

@job('shells')
def start_shell(shell_id):
    from joystick.app import app
    from joystick.models import Command, db
    import threading, socket, os
    import pexpect
    import socket

    shell = Command.query.get(shell_id)

    if os.path.exists(shell.socket): os.remove(shell.socket)
    sockin = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sockin.bind(shell.socket)
    os.chmod(shell.socket, 0o777)
    sockin.listen(1)

    child = pexpect.spawn(shell.cmd)
    logfile = open(shell.log_file, 'a')
    child.logfile = logfile

    shell.pid = child.pid
    db.session.add(shell)
    db.session.commit()

    while child.isalive():
        conn, addr = sockin.accept()
        conn.setblocking(0)
        while True:
            try:
                indata = conn.recv(1024)
                if indata:
                    child.write(indata)
                else:
                    break
            except socket.error:
                pass
            outdata = None
            try:
                outdata = child.read_nonblocking(4000, 0.01)
            except pexpect.TIMEOUT:
                pass
            if outdata:
                try:
                    conn.sendall(outdata)
                except socket.error:
                    break
        conn.close()
