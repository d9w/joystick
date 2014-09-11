from .app import app
from .models import db, Console, Command, ButtonCommand, LoopCommand
from .forms import ConsoleForm, ButtonForm, LoopForm
from flask import flash, request, redirect, url_for, render_template, Response
from werkzeug.exceptions import NotFound
from datetime import datetime

def get_or_404(klass, **query):
    instance = klass.query.filter_by(**query).first()
    if not instance:
        raise NotFound()
    return instance

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ConsoleForm()
    if request.method == 'POST' and form.validate():
        console = Console(name=form.name.data)
        db.session.add(console)
        db.session.commit()
        flash('Console {} added'.format(form.name.data), 'info')
    return render_template('index.html', consoles=Console.query.all(), form=form)

@app.route('/console/<console_name>', methods=['GET', 'POST'])
def console(console_name):
    console = get_or_404(Console, name=console_name)
    console.buttons.sort(key = lambda x: x.id)
    console.loops.sort(key = lambda x: x.id)
    console_form = ConsoleForm()
    button_form = ButtonForm()
    loop_form = LoopForm()
    if request.method == 'POST':
        if request.form['type'] == 'console':
            if console_form.validate():
                old_name = console.name
                console.name = console_form.name.data
                db.session.add(console)
                db.session.commit()
        elif request.form['type'] == 'button':
            if button_form.validate():
                button = ButtonCommand(cmd=button_form.cmd.data, console_id=console.id)
                db.session.add(button)
                db.session.commit()
        elif request.form['type'] == 'loop':
            if loop_form.validate():
                start_date = loop_form.start_date.data
                if not start_date:
                    start_date = (datetime.utcnow()-datetime.utcfromtimestamp(0)).total_seconds()
                loop = LoopCommand(cmd=loop_form.cmd.data, interval=float(loop_form.interval.data),
                        start_date=start_date, console_id=console.id)
                db.session.add(loop)
                db.session.commit()
    return render_template('console.html', console=console,
            console_form=console_form, button_form=button_form, loop_form=loop_form)

@app.route('/console/<console_name>/delete', methods=['POST'])
def console_delete(console_name):
    console = get_or_404(Console, name=console_name)
    db.session.delete(console)
    db.session.commit()
    flash('Console {} deleted'.format(console_name), 'info')
    return redirect(url_for('index'))

@app.route('/command/<command_id>', methods=['POST'])
def command(command_id):
    command = Command.query.get(command_id)
    console_name = command.console.name
    if request.form['action']=='push':
        command.push()
    elif request.form['action']=='stop':
        command.stop()
    elif request.form['action']=='log':
        return redirect(url_for('command_log', command_id=command_id))
    elif request.form['action']=='delete':
        command.delete()
        db.session.delete(command)
        db.session.commit()
    elif request.form['action']=='schedule':
        command.start()
    return redirect(url_for('console', console_name=console_name))

@app.route('/command/<command_id>/log', methods=['GET'])
def command_log(command_id):
    command = Command.query.get(command_id)
    return Response(command.get_log(), content_type='text/plain;charset=UTF-8')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/help', methods=['GET'])
def help():
    return render_template('help.html')

@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/forbidden_page.html"), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/page_not_found.html"), 404

@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/server_error.html"), 500
