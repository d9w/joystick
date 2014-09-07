from .app import app
from .models import ButtonCommand
from flask import Flask, Response, request, render_template, url_for, redirect
from flask.ext.socketio import SocketIO, emit
from threading import Thread
import time

socketio = SocketIO(app)

#TODO: handle thread referencing with something like RQ, celery, or circus
thread=None

def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        time.sleep(0.1)
        with open('/prod/joystick/testlog','r') as log_file:
            lines = log_file.readlines()
        socketio.emit('log', {'lines': ''.join(lines[max(len(lines)-5,0):])}, namespace='/test')

@socketio.on('open log', namespace='/test')
def open_log(message):
    # id in message.id
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()

@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)

@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': session['receive_count']})

@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': session['receive_count']})

@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
