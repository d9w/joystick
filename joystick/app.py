from flask import Flask, render_template

from .extensions import db, mail, cache, login_manager, principal

app = Flask('joystick')

app.config.from_pyfile('config.py')
app.config.from_pyfile(app.config['PRODUCTION_ROOT'] + '/production.cfg')

# extensions
db.init_app(app)
mail.init_app(app)
cache.init_app(app)
login_manager.setup_app(app)
principal.init_app(app)

@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/forbidden_page.html"), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/page_not_found.html"), 404

@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/server_error.html"), 500
