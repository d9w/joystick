from .app import app
from .models import Command
from flask import Flask, Response, request, render_template, url_for, redirect, session
from flask.ext.socketio import SocketIO, emit
import gevent
import time

socketio = SocketIO(app)

greenlets = {}

def serve_log(filename, cmd_id):
    print 'SERVING LOG FROM {} FOR COMMAND ID {}'.format(filename, cmd_id)
    while True:
        time.sleep(0.1)
        with open(filename,'r') as log_file:
            lines = log_file.readlines()
        socketio.emit('log', {'id': cmd_id, 'lines': ''.join(lines[max(len(lines)-5,0):])}, namespace='/test')

@socketio.on('open log', namespace='/test')
def open_log(message):
    command = Command.query.get(message['id'])
    greenlets['serving-{}'.format(command.id)] = gevent.spawn(serve_log, command.log_file, command.id)

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
    # check for existing greenlets for all commands in console
    # start them if they aren't already started
    emit('my response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    for key, greenlet in greenlets.iteritems():
        print 'killing {}'.format(key)
        greenlet.kill()
    print('Client disconnected')
