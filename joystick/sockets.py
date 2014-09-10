from .app import app
from .models import Command, Console
from flask import Flask, Response, request, render_template, url_for, redirect, session
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
import gevent
import time

socketio = SocketIO(app)

greenlets = {}

def serve_log(filename, cmd_id):
    while True:
        time.sleep(0.1)
        with open(filename,'r') as log_file:
            lines = log_file.readlines()
        socketio.emit('log', {'id': cmd_id, 'lines': ''.join(lines[max(len(lines)-5,0):])}, namespace='/test', room='testroom')

@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    console = Console.query.get(1)
    for button in console.buttons:
        if button.is_running():
            if 'serving-{}'.format(button.id) not in greenlets.keys():
                greenlets['serving-{}'.format(button.id)] = gevent.spawn(serve_log, button.log_file, button.id)

@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    if message['room'] not in socketio.rooms.keys():
        console = Console.query.get(1)
        for button in console.buttons:
            try:
                greenlets.pop('serving-{}'.format(button.id)).kill()
            except KeyError:
                pass
