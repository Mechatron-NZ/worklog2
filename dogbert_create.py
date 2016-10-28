import datetime
from peewee import *

import time_sheets
from tools import clear_screen


class DogbertCreate:
    time_format = "%d-%m-%Y"
    date_str = "DD-MM-YYYY"

    def date_format(self):
        """
        Menu that allows the format of the date to be changed to either MM-DD-YYYY or DD-MM-YYYY
        :return: None
        """
        clear_screen()

        while True:
            print(""" Time format
        (1) DD-MM-YYYY
        (2) MM-DD-YYYY
        """)
            option = input("please select an option: ")
            if option == "1" or option == "(1)":
                self.time_format = "%d-%m-%Y"
                self.date_str = "DD-MM-YYYY"
                clear_screen()
                break

            elif option == "2" or option == "(2)":
                self.time_format = "%m-%d-%Y"
                self.date_str = "MM-DD-YYYY"
                clear_screen()
                break

            else:
                clear_screen()
                print("you need to select an option from the list")

    @staticmethod
    def map_model_to_dict(entry=None):
        """converts a TimeSheet model into a dict or returns an empty model"""
        if entry is None:
            return {'username': None,
                    'project': None,
                    'task': None,
                    'date': None,
                    'duration': None,
                    'notes': None}
        else:
            return {'username': entry.username,
                    'project': entry.project,
                    'task': entry.task,
                    'date': entry.date,
                    'duration': entry.duration,
                    'notes': entry.notes}

    @staticmethod
    def list_users():
        """makes a multi-line string of all usernames"""
        all_users = time_sheets.Users.select()
        view_users = 'Users: '
        max_length = 50
        # list all users so you don't have to guess their names
        for entry in all_users:
            if entry.username != 'dogbert':  # hide admin superuser
                if len(view_users) >= max_length:
                    max_length += 50
                    view_users = view_users + '\n       ' + entry.username + '  '
                else:
                    view_users = view_users + entry.username + '  '
        return view_users

    @staticmethod
    def get_user(current_user, previous=None):
        """choose a user for this entry from user input"""
        if previous is not None:
            print("(Leave blank to keep previous)")
        else:
            print("(Leave blank for self)")

        choose_user = input("Choose the user for this entry: ")
        if choose_user == "":
            if previous is None:
                return current_user
            else:
                return previous
        else:
            try:
                time_sheets.Users.get(time_sheets.Users.username == choose_user.lower())
            except DoesNotExist:
                clear_screen()
                print("user does not exist try again\n\n")
                return None
            else:
                return choose_user

    @staticmethod
    def get_project(previous=None):
        """get the project number through user input"""
        if previous is not None:
            print("(Leave blank to keep previous)")

        project_string = input("please enter your five digit project number: ")

        if project_string.isdigit():
            if len(project_string) != 5:
                clear_screen()
                print("Project identifier must be a 5 digit number!")
                print("If you do not currently have a project number consult Doc Control Guidelines section 3(c)")
                return None
            else:
                return int(project_string)
        else:
            if project_string == "" and previous is not None:
                return previous
            clear_screen()
            print("Project identifier must be a 5 digit number!")
            print("If you do not currently have a project number consult Doc Control Guidelines section 3(c)")
            return None

    @staticmethod
    def get_task(previous=None):
        """get the task through user input"""
        if previous is not None:
            print("(Leave blank to keep previous)")

        task = input("What task have you been performing? ")
        # self.keywords(task)
        if task == "":
            if previous is None:
                print("task required")
                return None
            else:
                return previous
        else:
            return task

    def get_date(self, previous=None):
        """get the date through user input"""
        if previous is not None:
            print("(Leave blank to keep previous)")
        else:
            print("(Leave blank for today's date)")

        date_text = input("please enter a date {} for the task: ".format(self.date_str))
        if date_text == "":
            if previous is None:
                return datetime.date.today()
            else:
                return previous
        else:
            try:
                date = datetime.datetime.strptime(date_text, self.time_format)
            except ValueError:
                clear_screen()
                print("please follow {} format for date".format(self.time_format))
                return None
            else:
                return date

    @staticmethod
    def get_duration(previous=None):
        """get the duration through user input"""
        if previous is not None:
            print("(Leave blank to keep previous)")

        duration = input("please enter the duration of the task in minutes: ")

        if duration == "":
            clear_screen()
            return previous

        elif duration.isdigit():
            clear_screen()
            return int(duration)

        else:
            clear_screen()
            print("duration must be a number")
            return None

    @staticmethod
    def get_notes(previous):
        """get the notes through user input"""
        if previous is not None:
            print("(Leave blank to keep previous)")
            print("Multi-line comment leave a blank line to end note: ")
        else:
            print("Multi-line comment leave a blank line to end note: ")

        notes = ""
        while True:
            new_comment = input("")

            if new_comment == "":
                if notes == "":
                    if previous is None:
                        clear_screen()
                        print("comments required")
                        return None
                    else:
                        clear_screen()
                        return previous
                else:
                    clear_screen()
                    return notes
            else:
                if notes == "":
                    notes = notes + new_comment
                else:
                    notes = notes + '\n' + new_comment

    def task_entry(self, current_user, access, prev_entry=None):
        """
        creates new entry from user input that is added to the database
        """

        previous = self.map_model_to_dict(prev_entry)
        new_user = None
        while new_user is None:
            if access == 'admin' or access == 'manager':
                print(self.list_users())
                new_user = self.get_user(current_user, previous['username'])
            else:
                new_user = current_user

        new_project = None
        while new_project is None:
            new_project = self.get_project(previous['project'])

        new_task = None
        while new_task is None:
            new_task = self.get_task(previous['task'])

        new_date = None
        while new_date is None:
            new_date = self.get_date(previous['date'])

        new_duration = None
        while new_duration is None:
            new_duration = self.get_duration(previous['duration'])

        new_notes = None
        while new_notes is None:
            new_notes = self.get_notes(previous['notes'])

        return {'username': new_user,
                'project': new_project,
                'task': new_task,
                'date': new_date,
                'duration': new_duration,
                'notes': new_notes}
