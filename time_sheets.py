import os

from peewee import *
from passlib.hash import bcrypt_sha256

from tools import BASE_DIR
DATABASE_NAME = os.path.join(BASE_DIR, 'db', 'time_sheets.db')
db = SqliteDatabase(DATABASE_NAME)



class Users(Model):
    """User List"""
    username = CharField(max_length=255, unique=True)
    password = CharField(max_length=255)
    access = CharField(max_length=255, default='minion')

    class Meta:
        database = db


class TimeSheets(Model):
    """time sheet entries"""
    username = CharField(max_length=255)
    project = IntegerField()
    task = CharField(max_length=255)
    date = DateField()
    duration = IntegerField(constraints=[Check('duration > 0')])
    notes = TextField()

    class Meta:
        database = db


def initialize():
    """initialize time_sheets db create tables"""
    db.connect()
    db.create_tables([TimeSheets, Users], safe=True)


def create_user(username, password, access='minion'):
    """
    if username does not exist creates a new user with username password and access (default=minion)
    username is not encrypted

    password encryption is salt and hash with bcrypt_sha256
    12 rounds iterative hash with individual salt. hash is truncated and stored with salt in single variable
    """
    try:
        Users.get(Users.username == username)
    except DoesNotExist:
        pass_hashed = bcrypt_sha256.encrypt(password, rounds=12)
        new_user = Users.create(username=username, password=pass_hashed, access=access)
        return True
    else:
        print("user already exists")
        return False


def verify_login(username, password):
    """check username and password"""
    try:
        user = Users.get(Users.username == username)
    except DoesNotExist:
        print("user does not exist")
        return False
    else:
        return bcrypt_sha256.verify(password, user.password)  # verify given pass against hash value 'True' if success


def create_entry(username, task, project, date, duration, notes):
    """create a time sheet entry"""
    return TimeSheets.create(username=username, project=project, task=task, date=date, duration=duration, notes=notes)


def delete_user(username):
    """fire a user"""
    try:
        user = Users.get(Users.username == username)
    except DoesNotExist:
        print("{} not existing name".format(username))
        return False
    else:
        user.delete_instance()  # your fired
        return True

