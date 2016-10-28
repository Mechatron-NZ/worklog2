import datetime
import unittest
from unittest.mock import patch
from unittest import mock

import tools
import time_sheets
import dogbert_log


class OtherTests(unittest.TestCase):
    def setUp(self):
        self.test_log = dogbert_log.DogbertLog()
        self.has_exit = False

    def mock_exit(self):
        self.has_exit = True

    def test_exit(self):
        with patch('sys.exit', self.mock_exit):
            tools.my_exit()
            self.assertTrue(self.has_exit)


class UserTests(unittest.TestCase):
    def setUp(self):
        self.password = 'testi4ngtestr4and4omsc4rible'
        self.username = 'test_account'
        self.username2 = 'test_account2'
        self.test_log = dogbert_log.DogbertLog()
        self.entry = {'username': self.username,
                      'password': self.password}
        time_sheets.create_user(self.username, self.password, 'admin')

    def tearDown(self):
        try:
            time_sheets.delete_user(self.username)
            time_sheets.delete_user(self.username2)
        except time_sheets.Users.DoesNotExist:
            pass  # its gone because that's what the test did or we didn't make one
        else:
            pass  # cool thanks

    def mock_entry_input(self, prompt):
        if 'username' in prompt.lower():
            return self.entry['username']
        elif 'password' in prompt.lower():
            return self.entry['password']
        else:
            return ""

    def test_create_account(self):
        self.assertFalse(time_sheets.create_user(self.username, self.password, 'admin'))  # already exists
        self.assertTrue(time_sheets.create_user(self.username2, self.password, 'admin'))
        try:
            time_sheets.Users.get(time_sheets.Users.username == self.username2)
        except time_sheets.Users.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertTrue(True)

    def test_password(self):
        test_user_password = time_sheets.Users.get(time_sheets.Users.username == self.username).password
        self.assertNotEqual(test_user_password, self.password)

    def test_login_fail(self):
        self.entry['username'] = self.username
        self.entry['password'] = 'wrong_password'
        with patch('builtins.input', self.mock_entry_input):
            self.assertFalse(self.test_log.login())

        self.entry['username'] = 'wrong_username'
        self.entry['password'] = self.password

        with patch('builtins.input', self.mock_entry_input):
            self.assertFalse(self.test_log.login())

        self.entry['username'] = 'wrong_username'
        self.entry['password'] = 'wrong_password'

        with patch('builtins.input', self.mock_entry_input):
            self.assertFalse(self.test_log.login())

    def test_login_pass(self):
        with patch('builtins.input', self.mock_entry_input):
            self.assertTrue(self.test_log.login())

    def test_delete_user(self):
        self.assertTrue(time_sheets.delete_user(self.username))
        try:
            time_sheets.Users.get(time_sheets.Users.username == self.username)
        except time_sheets.Users.DoesNotExist:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        self.assertFalse(time_sheets.delete_user(self.username))


class EntryTests(unittest.TestCase):
    def setUp(self):
        self.test_log = dogbert_log.DogbertLog()
        self.test_log.current_user = 'unittest'
        self.test_log.access = 'admin'
        self.time_format = "%d-%m-%Y"
        self.password = 'twosquirlle8sju7mpi5ngwi3ld1ly'
        self.entry = {'username': (generate for generate in ["not a user", ""]),
                      'project': (generate for generate in ["not a number", "1234", "12345"]),
                      'task': (generate for generate in ["", "task"]),
                      'date': (generate for generate in ["not a date", "99-99-2016", ""]),
                      'duration': (generate for generate in ["not a number", "30"]),
                      'notes': (a_note for a_note in ["", "note", "note", ""])}
        time_sheets.create_user('unittest', self.password, 'admin')
        time_sheets.create_user('unittest2', self.password, 'admin')
        self.entry_model = time_sheets.create_entry('unittest',
                                                    'existing entry',
                                                    12345,
                                                    datetime.datetime.strptime('10-10-2010', "%d-%m-%Y"),
                                                    60,
                                                    'notes')
        self.entry2 = (a_note for a_note in ["note", "note", ""])
        self.entry3 = (a_note for a_note in ["d", "menu"])

    def tearDown(self):
        time_sheets.delete_user('unittest')
        time_sheets.delete_user('unittest2')
        time_sheets.TimeSheets.delete().where((time_sheets.TimeSheets.username == 'unittest') |
                                              (time_sheets.TimeSheets.username == 'UnitTest') |
                                              (time_sheets.TimeSheets.username == 'unittest2') |
                                              (time_sheets.TimeSheets.username == 'pleb')).execute()

    def mock_entry_input(self, prompt):
        if 'choose the user' in prompt.lower():
            return next(self.entry['username'])
        elif 'project' in prompt.lower():
            return next(self.entry['project'])
        elif 'what task' in prompt.lower():
            return next(self.entry['task'])
        elif 'date' in prompt.lower():
            return next(self.entry['date'])
        elif 'duration' in prompt.lower():
            return next(self.entry['duration'])
        elif '' == prompt.lower():
            return next(self.entry['notes'])

    def mock_entry_input2(self, prompt):
        if 'choose the user' in prompt.lower():
            return 'unittest2'
        elif 'project' in prompt.lower():
            return '54321'
        elif 'what task' in prompt.lower():
            return 'what task'
        elif 'date' in prompt.lower():
            return '11-11-2011'
        elif 'duration' in prompt.lower():
            return '42'
        elif 'delete' in prompt.lower():
            return next(self.entry3)
        elif '' == prompt:
            return next(self.entry2)


    def test_new_entries(self):
        with patch('builtins.input', self.mock_entry_input):
            new_entry = self.test_log.task_entry('unittest', 'admin')
            self.assertTrue(new_entry['username'] == self.test_log.current_user)
            self.assertTrue(new_entry['project'] == 12345)
            self.assertTrue(new_entry['task'] == 'task')
            self.assertTrue(new_entry['date'] == datetime.date.today())
            self.assertTrue(new_entry['duration'] == 30)
            self.assertTrue(new_entry['notes'] == 'note\nnote')

    def test_new_entry_minion(self):
        with patch('builtins.input', self.mock_entry_input2):
            new_entry = self.test_log.task_entry('pleb', 'minion')
            self.assertTrue(new_entry['username'] == 'pleb')

    def test_edit_no_change(self):
        with patch('builtins.input', return_value=""):
            edit_entry = self.test_log.task_entry('unittest', 'admin', self.entry_model)
            self.assertTrue(edit_entry['username'] == 'unittest')
            self.assertTrue(edit_entry['project'] == 12345)
            self.assertTrue(edit_entry['task'] == 'existing entry')
            self.assertTrue(edit_entry['date'] == datetime.datetime.strptime('10-10-2010', "%d-%m-%Y"))
            self.assertTrue(edit_entry['duration'] == 60)
            self.assertTrue(edit_entry['notes'] == 'notes')

    def test_edit(self):
        with patch('builtins.input', self.mock_entry_input2):
            edit_entry = self.test_log.task_entry('unittest', 'admin', self.entry_model)
            self.assertTrue(edit_entry['username'] == 'unittest2')
            self.assertTrue(edit_entry['project'] == 54321)
            self.assertTrue(edit_entry['task'] == 'what task')
            self.assertTrue(edit_entry['date'] == datetime.datetime.strptime('11-11-2011', "%d-%m-%Y"))
            self.assertTrue(edit_entry['duration'] == 42)
            self.assertTrue(edit_entry['notes'] == 'note\nnote')

    def test_edit_again(self):
        with patch('builtins.input', self.mock_entry_input2):
            self.test_log.edit(entry=self.entry_model)
            self.assertTrue(self.entry_model.username == 'unittest2')
            self.assertTrue(self.entry_model.project == 54321)
            self.assertTrue(self.entry_model.task == 'what task')
            self.assertTrue(self.entry_model.date == datetime.datetime.strptime('11-11-2011', "%d-%m-%Y"))
            self.assertTrue(self.entry_model.duration == 42)
            self.assertTrue(self.entry_model.notes == 'note\nnote')

    def mock_display(self, selected):
        self.assertGreater(len(selected), 0)
        self.assertTrue(selected[0].username == 'UnitTest')

    def test_create_entry(self):
        new_entry = {'username': 'UnitTest',
                     'project': 12345,
                     'task': 'task',
                     'date': datetime.datetime.strptime('25-05-2015', self.time_format),
                     'duration': 30,
                     'notes': "notes\nnotes"}
        with patch('dogbert_create.DogbertCreate.task_entry', return_value=new_entry):
            with patch('dogbert_log.DogbertLog.display', self.mock_display):
                self.test_log.new_entry()

    def test_display(self):
        with patch('builtins.input', self.mock_entry_input2):
            selected = [self.entry_model]
            self.test_log.display(selected)
            with self.assertRaises(time_sheets.TimeSheets.DoesNotExist):
                time_sheets.TimeSheets.get((time_sheets.TimeSheets.username == 'unittest') &
                                           (time_sheets.TimeSheets.task == 'existing entry'))


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.test_log = dogbert_log.DogbertLog()
        self.test_log.current_user = 'unittest'
        self.test_log.access = 'admin'
        self.password = 'twosquirlle8sju7mpi5ngwi3ld1ly'
        time_sheets.create_user('unittest', self.password, 'admin')
        self.entry_model = time_sheets.create_entry('unittest',
                                                    'unlikely_string_FDESW#$%G^%HRFT^$%',
                                                    98765,
                                                    datetime.datetime.strptime('10-10-2200', "%d-%m-%Y"),
                                                    7080,
                                                    'this is one')
        self.entry_model2 = time_sheets.create_entry('unittest',
                                                     'unlikely_string_asdas@#$@#$asD',
                                                     87654,
                                                     datetime.datetime.strptime('10-11-2200', "%d-%m-%Y"),
                                                     7081,
                                                     'this is two')
        self.entry = {'min': (generate for generate in ["not a number", "7080", "7080"]),
                      'max': (generate for generate in ["not a number", "", "7082"]),
                      'terms': (generate for generate in ["\w", "aegkljzd;fsogjad", 'this is one', 'unlikely_string_']),
                      'date': (generate for generate in ["not a date", "10-10-2010 05-05-2011 03-05-2016", "10-10-2200",
                                                         "10-09-2200" "10-12-2200"]),
                      'project': (generate for generate in ["fives", "123", '98765']),
                      'user': (generate for generate in ["not_a_user", "", "unittest"])}

    def tearDown(self):
        time_sheets.delete_user('unittest')
        time_sheets.TimeSheets.delete().where(time_sheets.TimeSheets.username == 'unittest').execute()

    def mock_entry_input(self, prompt):
        if 'range of dates' in prompt.lower():
            return next(self.entry['date'])
        elif 'minimum time' in prompt.lower():
            return next(self.entry['min'])
        elif 'maximum time' in prompt.lower():
            return next(self.entry['max'])
        elif 'enter your search' in prompt.lower():
            return next(self.entry['terms'])
        elif 'project number' in prompt.lower():
            return next(self.entry['project'])
        elif 'user to display' in prompt.lower():
            return next(self.entry['user'])

    def mock_display(self, selected):
        self.hold_result = selected

    def test_search_date(self):
        with patch('dogbert_log.DogbertLog.display', self.mock_display):
            with patch('builtins.input', self.mock_entry_input):
                self.test_log.search_date()
                length = len(list(self.hold_result))
                self.assertTrue(length == 1)
                self.assertTrue(self.hold_result[0].notes == "this is one")
                self.test_log.search_date()
                length = len(list(self.hold_result))
                self.assertTrue(length == 2)
                self.assertTrue(self.hold_result[0].notes == "this is one")
                self.assertTrue(self.hold_result[1].notes == "this is two")

    def test_search_duration(self):
        with patch('dogbert_log.DogbertLog.display', self.mock_display):
            with patch('builtins.input', self.mock_entry_input):
                self.test_log.search_duration()
                length = len(list(self.hold_result))
                self.assertTrue(length == 1)
                self.assertTrue(self.hold_result[0].notes == "this is one")
                self.test_log.search_duration()
                length = len(list(self.hold_result))
                self.assertTrue(length == 2)
                self.assertTrue(self.hold_result[0].notes == "this is one")
                self.assertTrue(self.hold_result[1].notes == "this is two")

    def test_search_term(self):
        with patch('dogbert_log.DogbertLog.display', self.mock_display):
            with patch('builtins.input', self.mock_entry_input):
                self.test_log.search_term()
                length = len(list(self.hold_result))
                self.assertTrue(length >= 2)
                self.test_log.search_term()
                length = len(list(self.hold_result))
                self.assertTrue(length == 0)
                self.test_log.search_term()
                length = len(list(self.hold_result))
                self.assertTrue(length == 1)
                self.assertTrue(self.hold_result[0].notes == "this is one")
                self.test_log.search_term()
                length = len(list(self.hold_result))
                self.assertTrue(length == 2)
                self.assertTrue(self.hold_result[0].notes == "this is one")
                self.assertTrue(self.hold_result[1].notes == "this is two")

    def test_search_project(self):
        with patch('dogbert_log.DogbertLog.display', self.mock_display):
            with patch('builtins.input', self.mock_entry_input):
                self.test_log.search_project()
                length = len(list(self.hold_result))
                self.assertTrue(length == 1)
                self.assertTrue(self.hold_result[0].notes == "this is one")

    def test_search_user(self):
        with patch('dogbert_log.DogbertLog.display', self.mock_display):
            with patch('builtins.input', self.mock_entry_input):
                self.test_log.search_by_user()
                length = len(list(self.hold_result))
                self.assertTrue(length == 2)
                self.assertTrue(self.hold_result[0].notes == "this is one")
                self.test_log.search_by_user()
                length = len(list(self.hold_result))
                self.assertTrue(length == 2)
                self.assertTrue(self.hold_result[0].notes == "this is one")
                self.assertTrue(self.hold_result[1].notes == "this is two")

if __name__ == "__main__":
    unittest.main()
