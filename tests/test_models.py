from tests import TestCase
from joystick.extensions import db
from joystick.models import Command

class TestCommand(TestCase):

    def test_make_command(self):

        command = Command()
        db.session.add(command)
        db.session.commit()

        assert command in db.session
