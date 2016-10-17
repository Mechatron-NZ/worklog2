from peewee import *
from passlib.hash import bcrypt_sha256

db = SqliteDatabase('time_sheets.db')


class Users(Model):
    """User List"""
    username = CharField(max_length=255, unique=True)
    password = CharField(max_length=255)
    access = CharField(max_length=255, default='minion')

    class Meta:
        database = db


class TimeSheets(Model):
    username = CharField(max_length=255)
    project = IntegerField()
    task = CharField(max_length=255)
    date = DateField()
    duration = IntegerField(constraints=[Check('duration > 0')])
    notes = TextField()

    class Meta:
        database = db


def initialize():
    db.connect()
    db.create_tables([TimeSheets, Users], safe=True)


def create_user(username, password, access='minion'):
    try:
        Users.get(Users.username == username)
    except DoesNotExist:
        pass_hashed = bcrypt_sha256.encrypt(password, rounds=12)  # 12 rounds iterative hash with individual salt
        Users.create(username=username, password=pass_hashed, access=access)
    else:
        print("user already exists")
        return 1


def verify_login(username, password):
    try:
        user = Users.get(Users.username == username)
    except DoesNotExist:
        print("user does not exist")
        return False
    else:
        return bcrypt_sha256.verify(password, user.password)  # verify given pass against hash value 'True' if success


def create_entry(username, task, project, date, duration, notes):
    TimeSheets.create(username=username, project=project, task=task, date=date, duration=duration, notes=notes)


def search():
    pass