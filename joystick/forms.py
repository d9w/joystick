from flask_wtf import Form
from wtforms import TextField, validators

from .models import Console

class ConsoleForm(Form):
    name = TextField('Name', [validators.Length(min=2, max=50),
        validators.NoneOf([c.name for c in Console.query.all()], message='Console name already exists')])
