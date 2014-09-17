from .app import app
from .models import Command, Console
from flask import Flask, Response, request, render_template, url_for, redirect, session
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
import gevent
import time
import pexpect
import socket

socketio = SocketIO(app)

greenlets = {}

sockets = {}

@socketio.on('connect', namespace='/shell')
def shell_connect():
    print 'CALLED CONNECT'

@socketio.on('open', namespace='/shell')
def shell_open():
    print 'CALLED OPEN'

@socketio.on('create', namespace='/shell')
def shell_create(cols=80, rows=24):
    socketio.emit('created', {'pty': None, 'id': 1}, namespace='/shell')
    print 'CALLED CREATE({},{})'.format(cols, rows)

@socketio.on('data', namespace='/shell')
def shell_data(id, data):
    sockets['shell-{}'.format(id)].sendall(data)
    print 'CALLED DATA({},{})'.format(id, data)

@socketio.on('kill', namespace='/shell')
def shell_kill(id):
    print 'CALLED KILL({})'.format(id)

@socketio.on('resize', namespace='/shell')
def shell_resize(id, cols=None, rows=None):
    print 'CALLED RESIZE({},{},{})'.format(id, cols, rows)

@socketio.on('process', namespace='/shell')
def shell_process(id, func=None):
    print 'CALLED PROCESS({},{})'.format(id, func)

@socketio.on('disconnect', namespace='/shell')
def shell_disconnect():
    print 'CALLED DISCONNECT'

@socketio.on('request paste', namespace='/shell')
def shell_paste(func):
    print 'CALLED PASTE({})'.format(func)

def serve_log(filename, cmd_id, console):
    while True:
        time.sleep(0.1)
        with open(filename,'r') as log_file:
            lines = log_file.readlines()
        socketio.emit('log', {'id': cmd_id, 'lines': ''.join(lines[max(len(lines)-5,0):])},
                namespace='/console', room=console)

def serve_shell(shell_id, console):
    while True:
        time.sleep(0.1)
        try:
            data = sockets['shell-{}'.format(shell_id)].recv(1024)
            socketio.emit('data', 1, data, namespace='/shell')
        except socket.error:
            pass

@socketio.on('join', namespace='/console')
def join(message):
    join_room(message['room'])
    console = Console.query.filter_by(name=message['room']).first()
    for button in console.buttons:
        if button.is_running():
            if 'serving-{}'.format(button.id) not in greenlets.keys():
                greenlets['serving-{}'.format(button.id)] = gevent.spawn(serve_log,
                        button.log_file, button.id, console.name)
    for shell in console.shells:
        if 'serving-{}'.format(shell.id) not in greenlets.keys():
            sockets['shell-{}'.format(shell.id)] = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sockets['shell-{}'.format(shell.id)].connect(shell.socket)
            sockets['shell-{}'.format(shell.id)].setblocking(0)
            greenlets['serving-{}'.format(shell.id)] = gevent.spawn(serve_shell,
                    shell.id, console.name)

@socketio.on('leave', namespace='/console')
def leave(message):
    leave_room(message['room'])
    if not socketio.rooms or ('/console' in socketio.rooms.keys()
            and message['room'] not in socketio.rooms['/console'].keys()):
        console = Console.query.filter_by(name=message['room']).first()
        for button in console.buttons:
            try:
                greenlets.pop('serving-{}'.format(button.id)).kill()
            except KeyError:
                pass
        for shell in console.shells:
            try:
                sockets.pop('shell-{}'.format(shell.id)).close()
                greenlets.pop('serving-{}'.format(shell.id)).kill()
            except KeyError:
                pass
