from flask.ext.script import Manager, Shell

from joystick.app import app
from joystick.models import Console, ShellCommand, LoopCommand, ButtonCommand, db

manager = Manager(app)

@manager.command
def run():
    app.run()

def init_data():
    console = Console(name='test')
    shell = ShellCommand(cmd='sh', console=console)
    loop = LoopCommand(cmd='uptime', console=console)
    button = ButtonCommand(cmd='reboot now', console=console)
    db.session.add_all([console, shell, loop, button])
    db.session.commit()

@manager.command
def initdb():

    db.drop_all()
    db.create_all()
    init_data()

@manager.shell
def _make_context():
    return dict(app=app, db=db)

if __name__ == '__main__':
    manager.run()
