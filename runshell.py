import sys, os
import pexpect
import threading
import socket

child = pexpect.spawn('ssh root@infinilab.infinidat.com')
logfile = open('/prod/joystick/shelllog', 'w')
child.logfile = logfile

socket_filename = '/prod/joystick/shellsocket_in'
if os.path.exists(socket_filename): os.remove(socket_filename)
sin = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sin.bind(socket_filename)
os.chmod(socket_filename, 0o777)
sin.listen(1)

socket_filename = '/prod/joystick/shellsocket_out'
if os.path.exists(socket_filename): os.remove(socket_filename)
sout = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sout.bind(socket_filename)
os.chmod(socket_filename, 0o777)
sout.listen(1)

def child_poll(sout, child):
    while child.isalive():
        conn, addr = sout.accept()
        while True:
            data = None
            try:
                data = child.read_nonblocking(4000, 0.1)
            except pexpect.TIMEOUT:
                pass
            if data:
                try:
                    conn.sendall(data)
                except socket.error:
                    break
        conn.close()

t = threading.Thread(target=child_poll, args=[sout, child])
t.start()

while child.isalive():
    conn, addr = sin.accept()
    while True:
        data = conn.recv(1024)
        if data:
            child.write(data)
        else:
            break
    conn.close()
