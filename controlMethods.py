from controlUserDB import USERS
from controlUserDB import PAY
import time

def add_user(user_id,username):
    try:
        USERS.create(user_id=user_id, username=username, status=0, timestamp=time.time(), tag='#'+username, teacher=0, teach='0')
    except Exception as e:
        print(e)
        return False

def edit_user(user_id=False, username=False, status=None, tag=None, teacher=None, teach=None):
    try:
        if user_id:
            row=USERS.get(USERS.user_id == user_id)
        elif username:
            row = USERS.get(USERS.username == username)

        if status != None:
            row.status = status

        if tag != None:
            row.tag = tag

        if teacher != None:
            row.teacher = teacher

        if teach != None:
            row.teach = teach

        row.save()
        return True
    except:
        return False


def add_log(user_id, count, none=False):
    try:
        if none:
            return PAY.create(timestamp=0, count=count, user_id=0, tag=user_id)
        else:
            return PAY.create(timestamp=time.time(), count=count, user_id=user_id, tag='0')
    except:
        return False
