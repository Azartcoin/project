import time
from peewee import *
db = SqliteDatabase('usersDB.db')


class USERS(Model):
    user_id = IntegerField()
    username = CharField()
    status = IntegerField()
    timestamp = IntegerField()
    tag = CharField()
    teacher = IntegerField()
    teach = CharField()

    class Meta:
        database = db

class PAY(Model):
    user_id = IntegerField()
    timestamp = IntegerField()
    count = IntegerField()
    tag = CharField()

    class Meta:
        database = db

db.connect()
USERS.create_table()
PAY.create_table()
