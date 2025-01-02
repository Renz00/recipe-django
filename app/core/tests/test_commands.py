""" Test custom Django management commands"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# use decorator for defining the method to be mocked for the test
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):

    def test_wait_for_db_ready(self, patched_check):
        """Test wait for database to be ready"""
        # when the mocked method is called, it will only return True
        patched_check.return_value = True

        call_command('wait_for_db')

        # check if the mocked method is called with the expected parameters
        patched_check.assert_called_once_with(databases=['default'])

    # The order of the mocked/patched methods is important.
    # First will always be the innermost patches.
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test wait for database when getting OperationalError"""
        # Mocking raised exceptions.
        # * 2 means that the exception will be raised twice.
        patched_check.side_effect = \
            [Psycopg2OpError] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
