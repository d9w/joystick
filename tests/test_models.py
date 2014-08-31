from tests import TestCase
from joystick.models import db, Command, ButtonCommand
from time import sleep

class TestButtons(TestCase):

    def test_button_create(self):

        button = ButtonCommand(cmd='uptime')
        db.session.add(button)
        db.session.commit()
        assert button in db.session

    def test_button_log(self):

        button = ButtonCommand(cmd='uptime')
        button.push()
        assert 'load' in button.get_log()

    def test_button_log_tail(self):

        button = ButtonCommand(cmd='for ((i=0; i<10; i++)); do echo $i; done')
        button.push()
        assert '9' in button.get_log_tail(5)
        assert '1' not in button.get_log_tail(5)

    def test_button_update(self):

        button = ButtonCommand(cmd='uptime')
        button.push()
        assert 'load' in button.get_log()
        button.cmd = 'ip addr'
        button.push()
        assert 'link' in button.get_log()

    # TODO: asynchronous calling
    def test_button_lock(self):

        print 'lock test'
        button = ButtonCommand(cmd='sleep 0') # asynchronous: sleep 3
        db.session.add(button)
        db.session.commit()
        button.push()
        print 'pushed'
        # assert button.locked
        assert not button.locked

    # TODO: asynchronous calling
    def ttest_button_delete(self):

        button = ButtonCommand(cmd='ping www.google.com -i 0.2')
        db.session.add(button)
        db.session.commit()

        push_button.delay(button.id)

        log_file = button.log_file
        assert open(log_file, 'r').read()

        db.session.delete(button)
        db.session.commit()

        assert button not in db.session

        sleep(1) # to make sure the process is killed and not pinging anymore

        try:
            open(log_file, 'r')
        except IOError:
            assert True
        #self.assertRaises(IOError, open(log_file))
