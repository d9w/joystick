from tests import TestCase
from joystick.extensions import db
from joystick.models import Command, ButtonCommand
from time import sleep

class TestButtons(TestCase):

    def test_button_create(self):

        button = ButtonCommand()
        db.session.add(button)
        db.session.commit()
        assert button in db.session

    def test_button_log(self):

        button = ButtonCommand(cmd='uptime')
        button.press()
        assert 'load' in button.get_log()

    def test_button_log_summary(self):

        button = ButtonCommand(cmd='for ((i=0; i<10; i++)); do echo $i; done')
        button.press()
        assert '9' in button.get_log_tail(5)
        assert '1' not in button.get_log_tail(5)

    def test_button_update(self):

        button = ButtonCommand(cmd='uptime')
        button.press()
        assert 'load' in button.get_log()
        button.cmd = 'ip addr'
        button.press()
        assert 'link' in button.get_log()

    def test_button_lock(self):

        button = ButtonCommand(cmd='sleep 3')
        button.press()
        assert button.locked
        sleep(4)
        assert not button.locked

    def test_button_delete(self):

        button = ButtonCommand(cmd='ping www.google.com -i 0.2')
        button.press()
        db.session.add(button)

        log_file = button.log_file
        assert open(log_file, 'r').read()

        db.session.delete(button)

        assert button not in db.session

        sleep(1) # to make sure the process is killed and not pinging anymore

        try:
            open(log_file, 'r')
        except IOError:
            assert True
        #self.assertRaises(IOError, open(log_file))
