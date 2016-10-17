import datetime
import unittest
from unittest.mock import patch


import time_sheets
import dogbert_log


class EntryTests(unittest.TestCase):
    def setUp(self):
        self.test_log = dogbert_log.DogbertLog()
        self.test_log.current_user = 'UnitTest'
        self.test_log.access = 'admin'
        self.time_format = "%d-%m-%Y"
        # date_str = "DD-MM-YYYY"
        self.entry = {'username': 'dogbert',
                      'project': '12345',
                      'task': 'task',
                      'date': '10-10-2010',
                      'duration': '30',
                      'notes': (a_note for a_note in ["note", "note", ""])}

    def mock_entry_input(self, prompt):
        if 'choose the user' in prompt.lower():
            return self.entry['username']
        elif 'project' in prompt.lower():
            return self.entry['project']
        elif 'what task' in prompt.lower():
            return self.entry['task']
        elif 'date' in prompt.lower():
            return self.entry['date']
        elif 'duration' in prompt.lower():
            return self.entry['duration']
        elif '' == prompt.lower():
            return next(self.entry['notes'])

    def test_new_entries(self):
        with patch('builtins.input', self.mock_entry_input):
            new_entry = self.test_log.create_entry()
            self.assertTrue(new_entry.username == self.entry['username'], self.entry['username'])
            self.assertTrue(new_entry.project == int(self.entry['project']), self.entry['project'])
            self.assertTrue(new_entry.task == self.entry['task'], self.entry['task'])
            self.assertTrue(new_entry.date == datetime.datetime.strptime(self.entry['date'], self.time_format),
                            self.entry['date'])
            self.assertTrue(new_entry.duration == int(self.entry['duration']), self.entry['duration'])


class SearchTests(unittest.TestCase):
    pass


class UserTests(unittest.TestCase):
    def setUp(self):
        self.password = 'testi4ngtestr4and4omsc4rible'
        self.username = 'test_account'

    def test_create_account(self):
        time_sheets.create_user(username=self.username, password=self.password)
        try:
           user_exists = time_sheets.Users.get(time_sheets.Users.username == self.username).username
        except time_sheets.Users.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def test_password(self):
        test_user_password = time_sheets.Users.get(time_sheets.Users.username == self.username).password
        self.assertNotEqual(test_user_password, self.password)

if __name__ == "__main__":
    unittest.main()


