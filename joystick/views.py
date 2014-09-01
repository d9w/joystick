from .app import app
from .models import db, Console
from .forms import ConsoleForm
from flask import flash, request, redirect, url_for, render_template

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ConsoleForm()
    if request.method == 'POST' and form.validate():
        print 'here'
        console = Console(name=form.name.data)
        db.session.add(console)
        db.session.commit()
        flash('Console {} added'.format(form.name.data))
    return render_template('index.html', consoles=Console.query.all(), form=form)

@app.route('/<console_name>', methods=['GET', 'POST'])
def console(console_name):
    console = Console.query.get(console_name)
    return render_template('console.html', console=console)

@app.route('/<console_name>/delete', methods=['POST'])
def console_delete(console_name):
    console = Console.query.get(console_name)
    db.session.delete(console)
    db.session.commit()
    return redirect(url_for('index'))

@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/forbidden_page.html"), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/page_not_found.html"), 404

@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/server_error.html"), 500
