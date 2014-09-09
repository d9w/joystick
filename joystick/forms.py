from flask_wtf import Form
from wtforms import TextField, HiddenField, DecimalField, validators

from .models import Console

def console_name_unique(form, field):
    if field.data in [c.name for c in Console.query.all()]:
        raise validators.ValidationError(message='Console name already exists')

class ConsoleForm(Form):
    type = HiddenField(default='console')
    name = TextField('Name', [validators.Required(), validators.Length(min=2, max=50), console_name_unique])

class CommandForm(Form):
    type = HiddenField(default='command')
    cmd = TextField('Command', [validators.Required(), validators.Length(min=1, max=255)])

class ButtonForm(CommandForm):
    type = HiddenField(default='button')
    pass

class LoopForm(CommandForm):
    type = HiddenField(default='loop')
    interval = DecimalField('Interval', [validators.Required(), validators.NumberRange(min=0)])
    start_date = DecimalField('Start', [validators.Optional()])
