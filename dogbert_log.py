import re
import datetime
import time

from peewee import *

import time_sheets
from tools import clear_screen, draw_file, my_exit


class DogbertLog:

    time_format = "%d-%m-%Y"
    date_str = "DD-MM-YYYY"
    current_user = None
    access = None

    def __init__(self):
        time_sheets.initialize()
        self.SEARCH_MENU = [{'key': '\n not an option', 'text': 'Search Menu', 'fn': None},
                            {'key': '1', 'text': '(1) Find by Date', 'fn': self.search_date},
                            {'key': '2', 'text': '(2) Find by Time Spent', 'fn': self.search_duration},
                            {'key': '3', 'text': '(3) Find by Keyword/s', 'fn': self.search_term},
                            {'key': '4', 'text': '(4) Find by Project', 'fn': self.search_project},
                            {'key': '5', 'text': '(5) Find by Employee', 'fn': self.search_by_user},
                            {'key': 'menu', 'text': '(menu) Return to Main Menu ', 'fn': print},
                            {'key': 'exit', 'text': '(exit) Quit program', 'fn': my_exit}]

        self.MAIN_MENU = [{'key': '\n not an option', 'text': 'Main Menu', 'fn': None},
                          {'key': '1', 'text': '(1) New Entry', 'fn': self.create_entry},
                          {'key': '2', 'text': '(2) Search', 'fn': self.menu_search},
                          {'key': '3', 'text': '(3) options', 'fn': self.options},
                          {'key': 'exit', 'text': '(exit) to quit program', 'fn': my_exit}]

    def login(self):
        while True:
            clear_screen()
            draw_file('login.txt')
            username = input('Username: ')
            password = input('Password: ')
            if time_sheets.verify_login(username=username, password=password):
                self.current_user = username
                self.access = time_sheets.Users.get(time_sheets.Users.username == username).access
                break
            else:
                input('User name or password fail press enter to try again: ')

    @staticmethod
    def menu(menu_list):
        flag = False
        while True:
            for option in menu_list:
                print(option['text'])
            choice = input()
            for option in menu_list:
                if option['key'] == choice.lower():
                    option['fn']()
                    flag = True
            clear_screen()
            if flag:
                break
            else:
                print('{} is not an option, please select from ( ) in menu'.format(choice))

    def create_entry(self):
        """
        creates new entry from user input that is added to the database
        """
        while True:
            if self.access == 'admin' or self.access == 'manager':
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
                print(view_users)

                choose_user = input("(leave blank for self) Choose the user for this time entry: ")
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
            else:
                user = self.current_user
                break

        while True:
            project_string = input("please enter your five digit project number: ")
            # self.keywords(duration)

            if project_string.isdigit():
                if len(project_string) != 5:
                    clear_screen()
                    print("Project identifier must be a 5 digit number!")
                    print("If you do not currently have a project number consult Doc Control Guidelines section 3(c)")
                else:
                    project = int(project_string)
                    break
            else:
                clear_screen()
                print("Project identifier must be a 5 digit number!")
                print("If you do not currently have a project number consult Doc Control Guidelines section 3(c)")

        while True:
            task = input("What task have you been performing? ")
            # self.keywords(task)
            if task == "":
                print("task required")
            else:
                break

        while True:
            date_text = input(
                "please enter a date for the task {} leave blank for today: ".format(self.date_str))
            # self.keywords(date_text)
            if date_text == "":
                date = datetime.date.today()
                break
            else:
                try:
                    date = datetime.datetime.strptime(date_text, self.time_format)
                except ValueError:
                    print("please follow {} format for date".format(self.date_str))
                else:
                    break

        while True:
            duration = input("please enter the duration of the task in minutes: ")
            # self.keywords(duration)

            if duration.isdigit():
                duration = int(duration)
                break
            else:
                print("duration must be a number")

        notes = ""
        print("please enter any comments leave a blank line to end note: ")
        while True:

            new_comment = input("")
            # self.keywords(new_comment)
            if new_comment == "":
                if notes == "":
                    clear_screen()
                    print("comments required")
                    print("please enter a comment leave a blank line to end note: ")
                else:
                    break
            else:
                if notes == "":
                    notes = notes + new_comment
                else:
                    notes = notes + '\n' + new_comment

        clear_screen()

        entry_date = date.strftime(self.time_format)

        entry = time_sheets.TimeSheets.create(username=user,
                                              project=project,
                                              task=task,
                                              date=date,
                                              duration=duration,
                                              notes=notes)

        new_entry = [entry.username, entry.project, entry.task, entry_date, entry.duration, entry.notes]

        input("""Entry added successfully
        User: {}
        Project: {}
        Task: {}
        Date: {}
        Duration: {}
        Comments: {}

        Press enter to continue""".format(*new_entry))
        clear_screen()
        return entry

    def edit(self, entry):
        """
        creates new entry dict from user input that is added to self.active_log and saved to CSV file
        :return: None
         """
        while True:
            if self.access == 'admin' or self.access == 'manager':
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
                print(view_users)

                choose_user = input("(Leave blank to keep previous) Choose the user for this time entry: ")
                if choose_user == "":
                    break
                else:
                    try:
                        time_sheets.Users.get(time_sheets.Users.username == choose_user.lower())
                    except DoesNotExist:
                        clear_screen()
                        print("user does not exist try again\n\n")
                    else:
                        entry.username = choose_user
                        break
            else:
                break

        while True:
            project_string = input("(Leave blank to keep previous) Please enter your five digit project number: ")

            if project_string == "":
                break
            elif project_string.isdigit():
                if len(project_string) != 5:
                    clear_screen()
                    print("Project identifier must be a 5 digit number!")
                    print("If you do not currently have a project number consult Doc Control Guidelines section 3(c)")
                else:
                    entry.project = int(project_string)
                    break
            else:
                clear_screen()
                print("Project identifier must be a 5 digit number!")
                print("If you do not currently have a project number consult Doc Control Guidelines section 3(c)")

        while True:
            task = input("(Leave blank to keep previous) What task have you been performing? ")
            # self.keywords(task)
            if task == "":
                break
            else:
                entry.task = task

        while True:
            date_text = input(
                "please enter a date for the task {} leave blank for previous: ".format(self.date_str))
            # self.keywords(date_text)
            if date_text == "":
                break  # leave as is
            else:
                try:
                    date = datetime.datetime.strptime(date_text, self.time_format)
                except ValueError:
                    print("please follow {} format for date".format(self.date_str))
                else:
                    entry.date = date
                    break

        while True:
            duration = input("(Leave blank to keep previous) Please enter the duration of the task in minutes: ")
            if duration == "":
                break
            elif duration.isdigit():
                entry.duration = int(duration)
                break
            else:
                print("duration must be a number")

        notes = ""
        print("(Leave fully blank to keep previous) Please enter any comments leave a blank line to end note: ")
        while True:
            new_comment = input("")
            # self.keywords(new_comment)
            if new_comment == "":
                if notes == "":
                    clear_screen()
                    break
                else:
                    entry.notes = notes
                    break
            else:
                if notes == "":
                    notes = notes + new_comment
                else:
                    notes = notes + '\n' + new_comment

        clear_screen()

        entry_date = date.strftime(self.time_format)

        new_entry = [entry.username, entry.project, entry.task, entry_date, entry.duration, entry.notes]
        entry.save()

        input("""Entry added successfully
        User: {}
        Project: {}
        Task: {}
        Date: {}
        Duration: {}
        Comments: {}

        Press enter to continue""".format(*new_entry))
        clear_screen()

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
        Comments: {}""".format((index + 1), len(selected), entry.username, entry.project, entry.task, entry_date, entry.duration, entry.notes))

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

####################################################################################

    def search_date(self):
        """
        Search all worklog entries by date. date is requested from the user with a given format.
        a single entry will look for a specific date two dates will look for a range of dates including given dates
        :return:
        """
        date_range = input("enter two dates a range of dates {} {} or a single date:".format(self.date_str,
                                                                                             self.date_str))
        dates = re.findall(r'\d{2}-\d{2}-\d{4}', date_range)

        if len(dates) < 1:
            clear_screen()
            print("no date entered or incorrect format")
            self.search_date()

        elif len(dates) == 1:
            datetime_new = datetime.datetime.strptime(dates[0], self.time_format)
            selected = (time_sheets.TimeSheets.select().where(time_sheets.TimeSheets.date == datetime_new)
                                                       .order_by(time_sheets.TimeSheets.date))
            self.display(selected)

        elif len(dates) == 2:
            datetime1 = datetime.datetime.strptime(dates[0], self.time_format)
            datetime2 = datetime.datetime.strptime(dates[1], self.time_format)
            selected = (time_sheets.TimeSheets.select().where((time_sheets.TimeSheets.date >= datetime1) &
                                                              (time_sheets.TimeSheets.date <= datetime2))
                                                       .order_by(time_sheets.TimeSheets.date))
            self.display(selected)

        else:
            clear_screen()
            print("too many dates given two dates are required for a range, one date for individual dates.")
            self.search_date()

    def search_duration(self):
        """
        searches the duration field of all worklog entries to see if they are within a range
        or match a specific duration. Determined by if one or two durations are given (min and max)
        :return: None
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
        searches for a string of characters or regex in a specified "field" of all worklog entries (default)
        alternatively searches for an exact match not case sensitive
        :return: None
        """

        find = input("enter your search terms: ")
        selected = (time_sheets.TimeSheets.select().where((time_sheets.TimeSheets.notes.regexp(find)) |
                                                          (time_sheets.TimeSheets.task.regexp(find)))
                                                   .order_by(time_sheets.TimeSheets.date))

        self.display(selected)

    def search_project(self):
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
        while True:
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
            print(view_users)

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

    def options(self):
        pass

    def menu_search(self):
        clear_screen()
        self.menu(self.SEARCH_MENU)

    def menu_main(self):
        while True:
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

if __name__ == "__main__":
    dogbert_diary = DogbertLog()
    dogbert_diary.login()
    dogbert_diary.menu_main()
