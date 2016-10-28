import re
import datetime

from peewee import *

from dogbert_create import DogbertCreate

import time_sheets
from tools import clear_screen, draw_file, my_exit


# note to tester user: dogbert password: $$$

class DogbertLog(DogbertCreate):

    current_user = None
    access = None

    def __init__(self):
        time_sheets.initialize()
        self.OPTIONS_MENU = [{'key': '\n not an option', 'text': 'Search Menu', 'fn': None},
                             {'key': '1', 'text': '(1) Create user', 'fn': self.create_user},
                             {'key': '2', 'text': '(2) Delete user', 'fn': self.delete_user},
                             {'key': '3', 'text': '(3) date format', 'fn': self.date_format},
                             {'key': 'exit', 'text': '(exit) Quit program', 'fn': my_exit}]

        self.SEARCH_MENU = [{'key': '\n not an option', 'text': 'Search Menu', 'fn': None},
                            {'key': '1', 'text': '(1) Find by Date', 'fn': self.search_date},
                            {'key': '2', 'text': '(2) Find by Time Spent', 'fn': self.search_duration},
                            {'key': '3', 'text': '(3) Find by Keyword/s', 'fn': self.search_term},
                            {'key': '4', 'text': '(4) Find by Project', 'fn': self.search_project},
                            {'key': '5', 'text': '(5) Find by Employee', 'fn': self.search_by_user},
                            {'key': 'menu', 'text': '(menu) Return to Main Menu ', 'fn': print},
                            {'key': 'exit', 'text': '(exit) Quit program', 'fn': my_exit}]

        self.MAIN_MENU = [{'key': '\n not an option', 'text': 'Main Menu', 'fn': None},
                          {'key': '1', 'text': '(1) New Entry', 'fn': self.new_entry},
                          {'key': '2', 'text': '(2) Search', 'fn': self.menu_search},
                          {'key': '3', 'text': '(3) options', 'fn': self.menu_options},
                          {'key': 'exit', 'text': '(exit) to quit program', 'fn': my_exit}]

    def create_user(self):
        """create new users"""
        if self.access == "admin":
            clear_screen()
            username = input('Username: ')
            try:
                user = time_sheets.Users.get(time_sheets.Users.username == username)
            except DoesNotExist:
                password = input('New Password: ')
                password2 = input('confirm Password: ')
                if password == password2:
                    print("access levels (1) Minion , (2) Manager, (3) Admin")
                    access_level = input('enter access level: ')
                    if access_level == '1':
                        access = 'minion'
                        print('access = minion')
                    elif access_level == '2':
                        access = 'manager'
                        print('access = manager')
                    elif access_level == '3':
                        access = 'admin'
                        print('access = admin')
                    else:
                        access = 'minion'
                        print('you should have typed a number you are now a minion')

                    time_sheets.create_user(username, password, access)
                    input('press enter to continue: ')
                else:
                    print("passwords don't match")
            else:
                print("user already exists")
        else:
            print("Access Denied! See Catbert evil director of HR for your punishment")

    def delete_user(self):
        """function that allows users to be removed"""
        if self.access == "admin":
            self.list_users()
            user = input("choose a user to fire: ")
            if user != 'dogbert':
                time_sheets.delete_user(user)
            else:
                print("nice try you can't fire me")
            if user == self.current_user:
                clear_screen()
                print("you fired yourself goodbye and good riddance")
                input("press enter to be ejected from the build")
                my_exit()
        else:
            print("Access Denied! See Catbert evil director of HR for your punishment")

    def login(self):
        """login screen for entering username and password calls the function that checks database"""
        while True:
            clear_screen()
            draw_file('login.txt')
            username = input('Username: ')
            password = input('Password: ')
            if time_sheets.verify_login(username=username, password=password):
                self.current_user = username
                self.access = time_sheets.Users.get(time_sheets.Users.username == username).access
                return True
            else:
                input('User name or password fail press enter to try again: ')
                return False

    @staticmethod
    def menu(menu_list):
        """re-useable menu takes a menu_list dict to display options and call functions"""
        flag = False
        while True:
            for option in menu_list:
                print(option['text'])
            choice = input("")
            for option in menu_list:
                if option['key'] == choice.lower():
                    option['fn']()
                    flag = True
            clear_screen()
            if flag:
                break
            else:
                print('{} is not an option, please select from ( ) in menu'.format(choice))

    def edit(self, entry):
        """calls function for user input to edit the existing TimeSheet model: entry saves changes to db"""
        clear_screen()
        entry_dict = self.task_entry(self.current_user, self.access, entry)
        entry.username = entry_dict['username']
        entry.project = entry_dict['project']
        entry.task = entry_dict['task']
        entry.date = entry_dict['date']
        entry.duration = entry_dict['duration']
        entry.notes = entry_dict['notes']
        entry.save()

    def new_entry(self):
        """calls functions to create a new time sheet entry, adds it to the database then displays it"""
        entry_dict = self.task_entry(self.current_user, self.access)
        entry = time_sheets.create_entry(**entry_dict)
        selected = []
        selected.append(entry)
        self.display(selected)

    def display(self, selected):
        """
        prints the contents of an individual entry, provides options for the deletion or editing of presented entry
        and allows forward and reverse scrolling through a sorted list of entries (newest first)
        :return: None
        """

        index = 0
        selected = list(selected)

        if len(selected) == 0:  # checks to see if the search list is empty (no matches)
            clear_screen()
            input("Nothing to display press enter to return to main menu: ")
            return None

        while True:
            clear_screen()
            entry_date = selected[index].date
            entry_date = entry_date.strftime(self.time_format)
            entry = selected[index]
            print("""entry {} of {}:
User: {}
Project: {}
Task: {}
Date: {}
Duration: {}
Comments: {}""".format((index + 1), len(selected), entry.username, entry.project, entry.task, entry_date,
                       entry.duration, entry.notes))

            options = input(
                "options:(exit) exit program, (menu) main menu,(E) Edit, (D) Delete, (P) Previous, [Enter] Next: ")
            if options.lower() == 'd' or options.lower() == 'delete':
                entry.delete_instance()
                del selected[index]

                if len(selected) == 0:  # checks to see if the search list is empty (no matches)
                    clear_screen()
                    input("Nothing to display press enter to return to main menu: ")
                    return None

            elif options.lower() == 'e' or options.lower() == 'edit':
                self.edit(entry)

            elif options.lower() == "" or options.lower() == "next":
                if index >= (len(selected) - 1):
                    index = 0
                else:
                    index += 1
            elif options.lower() == 'p' or options.lower() == 'previous':
                if index <= 0:
                    index = len(selected) - 1
                else:
                    index -= 1
            elif options.lower() == 'menu':
                break
            elif options.lower() == 'exit':
                my_exit()

    def menu_options(self):
        """runs a menu with option menu options"""
        clear_screen()
        self.menu(self.OPTIONS_MENU)

    def menu_search(self):
        """runs a menu with search menu options"""
        clear_screen()
        self.menu(self.SEARCH_MENU)

    def menu_main(self):
        """displays picture for current user if there is one opens a menu with main menu options"""
        clear_screen()
        dilbert_charaters = {'dilbert': 'dilbert.txt',
                             'alice': 'alice.txt',
                             'wally': 'wally.txt',
                             'asok': 'asok.txt',
                             'pointyhairedboss': 'pointyhairedboss.txt',
                             'catbert': 'catbert.txt',
                             'dogbert': 'dogbert.txt'}
        try:
            file = dilbert_charaters[self.current_user]
        except KeyError:
            pass
        else:
            draw_file(file)

        self.menu(self.MAIN_MENU)

    def search_date(self):
        """
        Search all worklog entries by date. date is requested from the user with a given format.
        a single entry will look for a specific date two dates will look for a range of dates including given dates
        :return: a query list of entries
        """
        while True:
            date_range = input("enter two dates a range of dates {} {} or a single date:".format(self.date_str,
                                                                                                 self.date_str))
            dates = re.findall(r'\d{2}-\d{2}-\d{4}', date_range)

            if len(dates) < 1:
                clear_screen()
                print("no date entered or incorrect format")

            elif len(dates) == 1:
                datetime_new = datetime.datetime.strptime(dates[0], self.time_format)
                selected = (time_sheets.TimeSheets.select().where(time_sheets.TimeSheets.date == datetime_new)
                            .order_by(time_sheets.TimeSheets.date))
                self.display(selected)
                break

            elif len(dates) == 2:
                datetime1 = datetime.datetime.strptime(dates[0], self.time_format)
                datetime2 = datetime.datetime.strptime(dates[1], self.time_format)
                selected = (time_sheets.TimeSheets.select().where((time_sheets.TimeSheets.date >= datetime1) &
                                                                  (time_sheets.TimeSheets.date <= datetime2))
                            .order_by(time_sheets.TimeSheets.date))
                self.display(selected)
                break

            else:
                clear_screen()
                print("too many dates given two dates are required for a range, one date for individual dates.")

    def search_duration(self):
        """
        searches the duration field of all worklog entries to see if they are within a range
        or match a specific duration. Determined by if one or two durations are given (min and max)
        :return: a query list of entries
        """

        clear_screen()
        is_range = True
        while True:
            min_time = input("please enter a minimum time for the task: ")
            if min_time.isdigit():
                min_time = int(min_time)
                break
            else:
                clear_screen()
                print("time must be numbers only:")

        clear_screen()
        while True:
            max_time = input("please enter a maximum time for the task " +
                             "or leave blank to search for a specific time: ")

            if max_time == "":
                is_range = False
                break
            elif max_time.isdigit():
                max_time = int(max_time)
                break
            else:
                clear_screen()
                print("time must be numbers only:")

        if is_range:
            selected = (time_sheets.TimeSheets.select()
                        .where((min_time <= time_sheets.TimeSheets.duration) &
                               (time_sheets.TimeSheets.duration <= max_time))
                        .order_by(time_sheets.TimeSheets.date))
        else:
            selected = (time_sheets.TimeSheets.select()
                        .where((min_time == time_sheets.TimeSheets.duration))
                        .order_by(time_sheets.TimeSheets.date))

        self.display(selected)

    def search_term(self):
        """
        searches for a string of characters or regex in notes or task fields of the timesheet db
        """

        find = input("enter your search terms: ")
        selected = (time_sheets.TimeSheets.select().where((time_sheets.TimeSheets.notes.regexp(find)) |
                                                          (time_sheets.TimeSheets.task.regexp(find)))
                    .order_by(time_sheets.TimeSheets.date))

        self.display(selected)

    def search_project(self):
        """seach timesheet db for projects matching a given number"""
        while True:
            project = input("please enter a project number: ")
            if len(project) == 5:
                if project.isdigit():
                    project = int(project)
                    break
                else:
                    clear_screen()
                    print("project must be numbers only:")
            else:
                clear_screen()
                print("project must be five digits")

        selected = time_sheets.TimeSheets.select().where(time_sheets.TimeSheets.project == project)

        self.display(selected)

    def search_by_user(self):
        """search times sheet entries by user"""
        while True:
            print(self.list_users())

            choose_user = input("(leave blank for self) Choose the user to display records: ")
            if choose_user == "":
                user = self.current_user
                break
            else:
                try:
                    time_sheets.Users.get(time_sheets.Users.username == choose_user.lower())
                except DoesNotExist:
                    clear_screen()
                    print("user does not exist try again\n\n")
                else:
                    user = choose_user
                    break
        selected = time_sheets.TimeSheets.select().where(time_sheets.TimeSheets.username == user)
        self.display(selected)

if __name__ == "__main__":
    dogbert_diary = DogbertLog()
    while not dogbert_diary.login():
        pass
    while True:
        dogbert_diary.menu_main()
