from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from config import *


def keyboardMain(admin=False):
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    if admin:
        nkb.row(InlineKeyboardButton('Добавить профит➕', callback_data=f'addprofit'),InlineKeyboardButton('Добавить пустой профит⭕', callback_data=f'add_none'))
        nkb.row(InlineKeyboardButton('Найти юзера🔎', callback_data=f'find_user'))
        nkb.row(InlineKeyboardButton('Личный кабинет👤', callback_data='lc'),
                InlineKeyboardButton('Наставники👨‍🏫', callback_data='teach_adm'))
        #nkb.row(InlineKeyboardButton('Изменить свой тег', callback_data=f'edit_tag'))
        nkb.row(InlineKeyboardButton('Чат💬', url=chat), InlineKeyboardButton('Канал выплат💰', url=channel))
        nkb.row(InlineKeyboardButton('👠Создать анкету', callback_data='sozd_ank'))
        nkb.row(InlineKeyboardButton('💳Изменить карту', callback_data='edit_card1'))
    else:
        #nkb.row(InlineKeyboardButton('Изменить свой тег', callback_data=f'edit_tag'))
        nkb.row(InlineKeyboardButton('Личный кабинет👤', callback_data='lc'), InlineKeyboardButton('Наставники', callback_data='teach'))
        nkb.row(InlineKeyboardButton('Чат💬',url=chat), InlineKeyboardButton('Канал выплат💰',url=channel))
        nkb.row(InlineKeyboardButton('👠Создать анкету', callback_data='sozd_ank'))
    return nkb


def keyboardCancel():
    nkb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    nkb.row(KeyboardButton('Отмена❌'))
    return nkb

def keyboardCancel_Skip():
    nkb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    nkb.row(KeyboardButton('Отмена❌'), KeyboardButton('Пропустить➡️'))
    return nkb


def keyboardAccept(user_id):
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    nkb.row(InlineKeyboardButton('Принять✅',callback_data=f'acc_yes{user_id}'),InlineKeyboardButton('Отказ❌',callback_data=f'acc_no{user_id}'))
    return nkb

def keyboardReq():
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    nkb.add(InlineKeyboardButton('Отправить заявку✅',callback_data='send_req'))
    return nkb

def keyboardFINISH():
    nkb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    nkb.row(KeyboardButton('Готово✅'),KeyboardButton('Отмена❌'))
    return nkb

def teach_keyboard(teachers):
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    for i in teachers:
        nkb.add(InlineKeyboardButton(i, callback_data=f'select_teach_{i}'))
    nkb.add(InlineKeyboardButton('Назад⬅️', callback_data='back'))
    return nkb


def keyboardAcceptTeacher(user_id):
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    nkb.row(InlineKeyboardButton('Принять✅',callback_data=f't_acc_yes{user_id}'),InlineKeyboardButton('Отказ❌',callback_data=f't_acc_no{user_id}'))
    return nkb

def keyboardBack():
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    nkb.row(InlineKeyboardButton('Назад',callback_data=f'back'))
    return nkb

def keyboardCard():
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    nkb.row(InlineKeyboardButton(f'@{verif}',url=f't.me/{verif}'))
    return nkb

def keyboardUnban(user_id):
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    nkb.row(InlineKeyboardButton('Unban', callback_data=f'unban_{user_id}'))
    return nkb

def keyboardUnmute(user_id):
    nkb = InlineKeyboardMarkup(resize_keyboard=True)
    nkb.row(InlineKeyboardButton('Unmute', callback_data=f'unmute_{user_id}'))
    return nkb
