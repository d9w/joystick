from flask_wtf import Form
from wtforms import TextField, validators

class ConsoleForm(Form):
    name = TextField('Name', [validators.Length(min=2, max=50)])
