from .app import app
from flask import render_template

@app.route('/')
def index():
    return 'Hello world!'

@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/forbidden_page.html"), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/page_not_found.html"), 404

@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/server_error.html"), 500
