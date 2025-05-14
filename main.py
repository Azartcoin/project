import random
from imgurpython import ImgurClient
from controlMethods import *
import logging
import asyncio
import time
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
import threading
import asyncio
import aiogram
from aiogram.types import ContentTypes, Message
from controlUserDB import USERS, PAY
from keyboards import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
import os
from datetime import datetime, timedelta
import threading
from aiogram.dispatcher.filters import Command
import requests
from pathlib import Path
from config import *

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
temp_user_db = {}
last_message_db = {}
card_text = 'Актуальной карты еще нету'
client = ImgurClient(client_id, client_secret)
IMAGE_DIR = "images"

class UserStates(StatesGroup):
    QUESTION1 = State()
    QUESTION2 = State()
    QUESTION3 = State()

    ADMIN_QUESTION0 = State()
    ADMIN_QUESTION1 = State()
    ADMIN_QUESTION2 = State()

    TAG_EDIT = State()
    CARD_EDIT = State()
    NEW_TEACH = State()
    GET_TEACH = State()
    USER_FIND = State()


class Anketa(StatesGroup):
    name = State()
    age = State()
    boobs = State()
    weight = State()
    height = State()
    city = State()
    clothing_size = State()
    shoe_size = State()
    h1_i_price = State()
    h1_you_price = State()
    h2_i_price = State()
    h2_you_price = State()
    night_h1_i_price = State()
    night_h1_you_price = State()
    full_night_i_price = State()
    full_night_you_price = State()
    photo = State()


@dp.callback_query_handler(text='find_user')
async def find_call(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    if callback.from_user.id in admins:
        last_message_db[callback.from_user.id] = await bot.send_message(callback.from_user.id, text='Введите юзернейм воркера без @', reply_markup=keyboardCancel())
        await UserStates.USER_FIND.set()



@dp.message_handler(state=UserStates.USER_FIND)
async def processUSER_FIND(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        try:
            user = USERS.get(USERS.username == message.text)
            user_id = user.user_id
            date = datetime.fromtimestamp(user.timestamp)
            current_date = datetime.fromtimestamp(time.time())
            days_in_team = (current_date - date).days
            count = [0, 0, 0]
            tag = user.tag
            for log in PAY.select():
                if log.user_id == user_id:
                    count[2] += log.count
                    tm = detect_time(log.timestamp)
                    if tm == 0:
                        count[0] += log.count
                        count[1] += log.count
                    if tm == 1:
                        count[1] += log.count
            if user.teacher:
                text = f'''
👤Профиль: _{user_id}_| *Учитель*
📆Количество дней в команде: _{days_in_team}_
👛Имя в выплатах: _{tag}_

💳 Сумма профитов:
└ За день: *{count[0]}* RUB 
└ За месяц: *{count[1]}* RUB 
└ За все время: *{count[2]}* RUB

'''
            else:
                if user.teach == '1':
                    text = f'''
👤Профиль: _{user_id}_
📆Количество дней в команде: _{days_in_team}_
👨‍🏫Наставник: _В ожидании..._
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: *{count[0]} RUB* 
└ За месяц: *{count[1]} RUB* 
└ За все время: *{count[2]} RUB*

            '''
                elif user.teach not in ('0', '2'):
                    text = f'''
👤Профиль: _{user_id}_
📆Количество дней в команде: _{days_in_team}_
👨‍🏫Наставник: _{USERS.get(USERS.username == user.teach).tag}_
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: *{count[0]} RUB* 
└ За месяц: *{count[1]} RUB* 
└ За все время: *{count[2]} RUB*

            '''
                else:
                    text = f'''
👤Профиль: _{user_id}_
📆Кол-во дней в команде: _{days_in_team}_
👨‍🏫Наставник: _Не выбран_
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: *{count[0]} RUB* 
└ За месяц: *{count[1]} RUB* 
└ За все время: *23{count[2]} RUB*'''
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id,text=text, reply_markup=keyboardCancel(),parse_mode="Markdown")
        except Exception as e:
            print(e)
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id,text='Такого пользователя нет в базе.\nВведите юзернейм',reply_markup=keyboardCancel())


async def show_main_menu(message):
    try:
        id = message.message.chat.id
    except:
        id = message.from_user.id
    try:
        await last_message_db[id].delete()
    except:
        pass
    try:
        status = USERS.get(USERS.user_id == id).status
        if status == 0:
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=id,text='Заявка находится на рассмотрении')
        elif status == 1:
            if id in admins:
                last_message_db[message.from_user.id] = await bot.send_message(id,text='Добро пожаловать! \r\nАдмин панель:', reply_markup=keyboardMain(True))
            else:
                last_message_db[message.from_user.id] = await bot.send_message(id, text='Добро пожаловать! \r\n ', reply_markup=keyboardMain())
        elif status == 2:
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=id,text='Заявка была отклонена')
    except Exception as e:
        temp_user_db[id] = ['', '', [], 'last_message']
        temp_user_db[id][3] = last_message_db[message.from_user.id] = await bot.send_message(id,text='Привет, отправь заявку!', reply_markup=keyboardReq())


def detect_time(timestamp):
    date = datetime.fromtimestamp(timestamp)
    current_date = datetime.now()
    if str(date).split(' ')[0] == str(current_date).split(' ')[0]:
        return 0
    elif str(date).split(' ')[0].split('-')[:-1] == str(current_date).split(' ')[0].split('-')[:-1]:
        return 1


@dp.callback_query_handler(text='back')
async def add_profit(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await state.finish()
    await show_main_menu(callback)

@dp.message_handler(commands='start')
async def main(message: types.Message):
    if message.from_user.id == message.chat.id:
        try:
            await last_message_db[message.from_user.id].delete()
        except:
            pass
        if message.from_user.username == None:
            await message.answer('Для использования бота необходимо добавить username в телеграмм профиль')
        else:
            await show_main_menu(message)


@dp.callback_query_handler(text='edit_card')
async def edit_card(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    if callback.from_user.id in admins:
        last_message_db[callback.from_user.id] = await bot.send_message(chat_id=callback.from_user.id, text=f'Введите новый текст card', reply_markup=keyboardCancel())
        await UserStates.CARD_EDIT.set()
        await callback.answer()


@dp.message_handler(state=UserStates.CARD_EDIT)
async def processEdit_card(message: types.Message,state: FSMContext):
    global card_text
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        card_text = message.text
        await bot.send_message(chat_id=message.from_user.id, text=f'Новый текст card установлен')
        await state.finish()
        await show_main_menu(message)



@dp.message_handler(commands='card')
async def chat_card(message: types.Message):
    msg = await message.answer(card_text, reply_markup=keyboardCard())
    await asyncio.sleep(10)
    await msg.delete()
    await message.delete()

@dp.message_handler(commands='help')
async def chat_card(message: types.Message):
    msg = await message.answer(help_text, parse_mode='HTML', disable_web_page_preview=True)
    await asyncio.sleep(10)
    await msg.delete()
    await message.delete()

@dp.message_handler(commands='mp')
async def chat_profile(message: types.Message):
    try:
        user = USERS.get(USERS.user_id == message.from_user.id)
        user_id = message.from_user.id
        count = [0, 0, 0]
        tag = user.tag
        for log in PAY.select():
            if log.user_id == user_id:
                count[2] += log.count
                tm = detect_time(log.timestamp)
                if tm == 0:
                    count[0] += log.count
                    count[1] += log.count
                if tm == 1:
                    count[1] += log.count
        if user.teacher:
            text = f'''
👤Профиль: <i>{user_id}</i> | <b>Учитель</b>
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: <b>{count[0]} RUB</b> 
└ За месяц: <b>{count[1]} RUB</b> 
└ За все время: <b>{count[2]} RUB</b>

'''
        else:
            if user.teach == '1':
                text = f'''
👤Профиль: <i>{user_id}</i>
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: <b>{count[0]} RUB</b> 
└ За месяц: <b>{count[1]} RUB</b> 
└ За все время: <b>{count[2]} RUB</b>

            '''
            elif user.teach not in ('0', '2'):
                text = f'''
👤Профиль: <i>{user_id}</i>
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: <b>{count[0]} RUB</b> 
└ За месяц: <b>{count[1]} RUB</b> 
└ За все время: <b>{count[2]} RUB</b>

            '''
            else:
                text = f'''
👤Профиль: <i>{user_id}</i>
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: <b>{count[0]} RUB</b> 
└ За месяц: <b>{count[1]} RUB</b> 
└ За все время: <b>{count[2]} RUB</b>

            '''
        msg = await message.answer(text,parse_mode="HTML")
        await asyncio.sleep(10)
        await msg.delete()
        await message.delete()
    except Exception as e:
        print(e)


@dp.message_handler(commands='Top')
async def Top(message: types.Message):
    db = {}
    for log in PAY.select():
        if log.tag == '0':
            try:
                db[USERS.get(USERS.user_id == log.user_id).tag] += log.count
            except:
                db[USERS.get(USERS.user_id == log.user_id).tag] = log.count
        else:
            try:
                db[log.tag] += log.count
            except:
                db[log.tag] = log.count
    db = {k: v for k, v in sorted(db.items(), key=lambda item: item[1], reverse=True)}
    text = '''<b>🏆 Топ воркеров за все время:</b>\n'''
    x = 0
    if len(db) > 0:
        for i in db:
            if x == 10:
                break
            if x == 0:
                l = '🥇'
            elif x == 1:
                l = '🥈'
            elif x == 2:
                l = '🥉'
            else:
                l = '🔸'
            text += f'\n{l} {i} - {db[i]} ₽'
            x += 1
    else:
        text += f'\n<i>Профитов еще не было</i>'
    text += f'\n\n<b>💸 Общий профит за все время: {sum(list(db.values()))} ₽</b>'
    msg = await message.answer(text,parse_mode="HTML")
    await asyncio.sleep(10)
    await msg.delete()
    await message.delete()


@dp.message_handler(commands='Topd')
async def Topd(message: types.Message):
    db = {}
    for log in PAY.select():
        if detect_time(log.timestamp) == 0 and log.tag == '0':
            try:
                db[USERS.get(USERS.user_id == log.user_id).tag] += log.count
            except:
                db[USERS.get(USERS.user_id == log.user_id).tag] = log.count
    db = {k: v for k, v in sorted(db.items(), key=lambda item: item[1], reverse=True)}
    text = '''<b>🏆 Топ воркеров за день:</b>\n'''
    x = 0
    if len(db) > 0:
        for i in db:
            if x == 10:
                break
            if x == 0:
                l = '🥇'
            elif x == 1:
                l = '🥈'
            elif x == 2:
                l = '🥉'
            else:
                l = '🔸'
            text += f'\n{l} {i} - {db[i]} ₽'
            x += 1
    else:
        text += f'\n<i>Сегодня профитов еще не было</i>'
    text += f'\n\n<b>💸 Общий профит за день: {sum(list(db.values()))} ₽</b>'
    msg = await message.answer(text,parse_mode="HTML")
    await asyncio.sleep(10)
    await msg.delete()
    await message.delete()

@dp.message_handler(commands='Topm')
async def Topm(message: types.Message):
    db = {}
    for log in PAY.select():
        if detect_time(log.timestamp) in (0, 1) and log.tag == '0':
            try:
                db[USERS.get(USERS.user_id == log.user_id).tag] += log.count
            except:
                db[USERS.get(USERS.user_id == log.user_id).tag] = log.count
    db = {k: v for k, v in sorted(db.items(), key=lambda item: item[1], reverse=True)}
    text = '''<b>🏆 Топ воркеров за месяц:</b>\n'''
    x = 0
    if len(db) > 0:
        for i in db:
            if x == 10:
                break
            if x == 0:
                l = '🥇'
            elif x == 1:
                l = '🥈'
            elif x == 2:
                l = '🥉'
            else:
                l = '🔸'
            text += f'\n{l} {i} - {db[i]} ₽'
            x += 1
    else:
        text += f'\n<i>Профитов за месяц еще не было</i>'
    text += f'\n\n<b>💸 Общий профит за месяц: {sum(list(db.values()))} ₽</b>'
    msg = await message.answer(text,parse_mode="HTML")
    await asyncio.sleep(10)
    await msg.delete()
    await message.delete()

@dp.callback_query_handler(text='send_req')
async def pr_call(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    try:
        status = USERS.get(USERS.user_id == callback.from_user.id).status
        await callback.answer('Заявка уже была отправлена. Ожидайте на рассмотрение!')
    except:
        last_message_db[callback.from_user.id] = await bot.send_message(chat_id=callback.from_user.id, text='Откуда узнали про нас?', reply_markup=keyboardCancel())
        await UserStates.QUESTION1.set()
        await callback.answer()

#q1
@dp.message_handler(state=UserStates.QUESTION1)
async def processQUESTION1(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        temp_user_db[message.from_user.id][0] = message.text
        last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Был ли опыт в данной сфере?', reply_markup=keyboardCancel())
        await UserStates.QUESTION2.set()

#q2
@dp.message_handler(state=UserStates.QUESTION2)
async def processQUESTION2(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        temp_user_db[message.from_user.id][1] = message.text
        last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Были ли профиты? если да, отправьте скриншот у виде файла', reply_markup=keyboardCancel_Skip())
        await UserStates.QUESTION3.set()

#q3
@dp.message_handler(state=UserStates.QUESTION3,content_types=[types.ContentType.DOCUMENT,types.ContentType.TEXT])
async def processQUESTION3(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await state.finish()
        await show_main_menu(message)
    elif message.text == 'Пропустить➡️':
        temp_user_db[message.from_user.id][2] = 'нет'
        add_user(message.from_user.id, message.from_user.username)
        last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Заявка отправлена и будет рассмотрена')
        await get_reqs(message, temp_user_db[message.from_user.id])
        await state.finish()
    elif message.text == 'Готово✅':
        id = message.from_user.id
        try:
            status = USERS.get(USERS.user_id == id).status
            if status == 0:
                last_message_db[message.from_user.id] = await bot.send_message(chat_id=id, text='Заявка находится на рассмотрении')
            elif status == 1:
                if id in admins:
                    last_message_db[message.from_user.id] = await bot.send_message(id, text='Добро пожаловать!', reply_markup=keyboardMain(True))
                else:
                    last_message_db[message.from_user.id] = await bot.send_message(id, text='Добро пожаловать!', reply_markup=keyboardMain())
            elif status == 2:
                last_message_db[message.from_user.id] = await bot.send_message(chat_id=id, text='Заявка была отклонена')
        except:
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Заявка отправлена и будет рассмотрена')
            add_user(message.from_user.id, message.from_user.username)
            await get_reqs(message, temp_user_db[message.from_user.id])
            await state.finish()
    elif message.document == None:
        last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Неизвестная команда.\nБыли ли профиты? если да, отправьте скриншот у виде файла', reply_markup=keyboardCancel_Skip())
    else:
        photo_path = f'profitsPhotos/{random.randint(100,10000000)}.jpg'
        await message.document.download(photo_path)
        temp_user_db[message.from_user.id][2].append(photo_path)
        last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Фото загружено. Нажми готово или отправь еще фото',
                               reply_markup=keyboardFINISH())


@dp.callback_query_handler(text='edit_tag')
async def edit_tag(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    if callback.from_user.id in admins:
        last_message_db[callback.from_user.id] = await bot.send_message(chat_id=callback.from_user.id, text=f'Введите новый тег', reply_markup=keyboardCancel())
        await UserStates.TAG_EDIT.set()
        await callback.answer()


@dp.callback_query_handler(text='teach_adm')
async def teach_adm(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    if callback.from_user.id in admins:
        last_message_db[callback.from_user.id] = await bot.send_message(chat_id=callback.from_user.id, text=f'Введите юзернейм учителя', reply_markup=keyboardCancel())
        await UserStates.NEW_TEACH.set()
        await callback.answer()

@dp.callback_query_handler(text='teach')
async def teach_adm(callback: types.CallbackQuery, state: FSMContext):
    if USERS.get(USERS.user_id == callback.from_user.id).teacher == 1:
        study = []
        username = USERS.get(USERS.user_id == callback.from_user.id).username
        for log in USERS.select():
            if log.teach == username:
                study.append(log.username)
        if len(study) == 0:
            await bot.send_message(chat_id=callback.from_user.id, text='У вас нет учеников')
        else:
            text = 'Ваши ученики:'
            for i in study:
                text += f'\n@{i}'
            max_message_length = 4096

            if len(text) >= max_message_length:
                parts = [text[i:i + max_message_length] for i in range(0, len(text), max_message_length)]
                for part in parts:
                    await bot.send_message(callback.from_user.id, part)
                    await asyncio.sleep(0.2)
            else:
                await bot.send_message(callback.from_user.id, text)
        await state.finish()
        await show_main_menu(callback)
        try:
            await callback.message.delete()
        except:
            pass
    else:
        if USERS.get(USERS.user_id == callback.from_user.id).teach == '0':
            teachers = []
            for log in USERS.select():
                if log.teacher == 1:
                    teachers.append(log.username)
            last_message_db[callback.from_user.id] = await bot.send_message(chat_id=callback.from_user.id, text=f'Выберите учителя', reply_markup=teach_keyboard(teachers))
        else:
            if USERS.get(USERS.user_id == callback.from_user.id).teach == '1':
                await bot.send_message(chat_id=callback.from_user.id, text=f'Вы уже подали одну заявку')
                await state.finish()
                await show_main_menu(callback)
            elif USERS.get(USERS.user_id == callback.from_user.id).teach == '2':
                await bot.send_message(chat_id=callback.from_user.id, text=f'У вас уже был учитель')
                await state.finish()
                await show_main_menu(callback)
            else:
                await bot.send_message(chat_id=callback.from_user.id, text=f'У вас уже есть учитель')
                await state.finish()
                await show_main_menu(callback)
        try:
            await callback.message.delete()
        except:
            pass



@dp.callback_query_handler(Text(startswith='select_teach_'))
async def acc_call(callback: types.CallbackQuery,state: FSMContext):
    teacher = USERS.get(USERS.username == callback.data.split('select_teach_')[1])
    user = USERS.get(USERS.user_id == callback.from_user.id)
    await bot.send_message(chat_id=teacher.user_id, text=f'{user.username} Выбрал вас в качестве учителя', reply_markup=keyboardAcceptTeacher(callback.from_user.id))
    edit_user(user_id=callback.from_user.id, teach='1')
    await bot.send_message(chat_id=callback.from_user.id, text=f'Вы подали заявку учителю.✅')
    try:
        await callback.message.delete()
    except:
        pass
    await state.finish()
    await show_main_menu(message)


@dp.message_handler(state=UserStates.GET_TEACH)
async def processGet_Teach(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await state.finish()
        await show_main_menu(message)
        return
    teachers = []
    for log in USERS.select():
        if log.teacher == 1:
            teachers.append(log.username)
    if message.text not in teachers:
        last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text=f'Неизвестный выбор. Выберите учителя:', reply_markup=teach_keyboard(teachers))
    else:
        teacher = USERS.get(USERS.username == message.text)
        user = USERS.get(USERS.user_id == message.from_user.id)
        await bot.send_message(chat_id=teacher.user_id, text=f'{user.username} Выбрал Вас в качестве учителя✅', reply_markup=keyboardAcceptTeacher(message.from_user.id))
        edit_user(user_id=message.from_user.id, teach='1')
        await bot.send_message(chat_id=message.from_user.id, text=f'Вы подали заявку учителю✅')
        await state.finish()
        await show_main_menu(message)


@dp.message_handler(state=UserStates.NEW_TEACH)
async def processTeach(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        try:
            user = USERS.get(USERS.username == message.text)
            if user.teacher:
                edit_user(username=message.text, teacher=0)
                await bot.send_message(chat_id=message.from_user.id, text='Учитель успешно удален✅')
            else:
                edit_user(username=message.text, teacher=1)
                await bot.send_message(chat_id=message.from_user.id, text='Учитель успешно добавлен✅')
            await bot.send_message(chat_id=user.user_id, text='Теперь вы учитель!👨‍🏫')
            await state.finish()
            await show_main_menu(message)
        except:
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Такого пользователя нет в базе.\nВведите юзернейм учителя👨‍🏫',
                                   reply_markup=keyboardCancel())


@dp.message_handler(state=UserStates.TAG_EDIT)
async def processTAG(message: types.Message, state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        try:
            USERS.get(USERS.tag == '#'+message.text.replace('#',''))
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id,
                                                                           text='Этот тег уже занят\nВведите тег', reply_markup=keyboardCancel())
        except:
            edit_user(user_id=message.from_user.id, tag='#'+message.text.replace('#',''))
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id,text='Тег успешно обновлен')
            await state.finish()
            await show_main_menu(message)

async def get_reqs(message,answers):
    try:
        username = message.message.chat.username
        id = message.message.chat.id
    except:
        username = message.from_user.username
        id = message.from_user.id
    text = f'НОВАЯ ЗАЯВКА\n@{username}\n1: {answers[0]}\n2: {answers[1]}'
    if answers[2] == 'нет':
        temp_user_db[message.from_user.id][3] = await bot.send_message(chat_id=admin_chat_id, text=text,reply_markup=keyboardAccept(id))
    else:
        print(temp_user_db[message.from_user.id][2])
        for photo in temp_user_db[message.from_user.id][2]:
            text += '\n'+client.upload_from_path(path=photo)['link']
        temp_user_db[message.from_user.id][3] = await bot.send_message(chat_id=admin_chat_id, text=text,reply_markup=keyboardAccept(id))

@dp.callback_query_handler(Text(startswith='acc'))
async def acc_call(callback: types.CallbackQuery):
    decision = callback.data
    if 'yes' in decision:
        edit_user(user_id=int(callback.data.split('yes')[1]), status=1)
        await temp_user_db[int(callback.data.split('yes')[1])][3].delete()
        await bot.send_message(chat_id=int(callback.data.split('yes')[1]), text='✅Ваша заявка принята. Добро пожаловать в команду!\n \nТы не знаешь с чего начать? У нас в команде есть *все материалы для твоего обучения.*\n \nВ боте ты *можешь выбрать себе наставника*, который поможет тебе почуствовать вкус первого профита и не потерять его по дороге.\n \n*Обязательно ознакомься со всем*, чтобы у тебя не возникало проблем во время ворка. \n \nЕсли же у тебя уже есть опыт, то *желаем побольше профитов!* \n \n*Пропиши /start чтобы открыть меню.*',parse_mode="Markdown")
    elif 'no' in decision:
        edit_user(user_id=int(callback.data.split('no')[1]), status=2)
        await bot.send_message(chat_id=int(callback.data.split('no')[1]), text='❌Ваша заявка отклонена')
        await temp_user_db[int(callback.data.split('no')[1])][3].delete()
    try:
        await callback.message.delete()
    except:
        pass

@dp.callback_query_handler(Text(startswith='t_acc'))
async def acc_call(callback: types.CallbackQuery, state: FSMContext):
    decision = callback.data
    if 'yes' in decision:
        edit_user(user_id=int(callback.data.split("_yes")[-1]), teach=USERS.get(USERS.user_id == callback.from_user.id).username)
        await bot.send_message(chat_id=int(callback.data.split("_yes")[-1]), text=f'Учитель принял вашу заявку✅')
        await bot.send_message(chat_id=callback.from_user.id, text=f'Вы приняли заявку✅')
        try:
            await callback.message.delete()
        except:
            pass
        await state.finish()
        await show_main_menu(callback)
    elif 'no' in decision:
        edit_user(user_id=int(callback.data.split("_no")[-1]), teach='0')
        await bot.send_message(chat_id=int(callback.data.split("_no")[-1]), text=f'Учитель отклонил вашу заявку❌')
        await bot.send_message(chat_id=callback.from_user.id, text=f'Вы отклонили заявку❌')
        try:
            await callback.message.delete()
        except:
            pass
        await state.finish()
        await show_main_menu(callback)


async def delete_message(message: types.Message):
    """Удаляет сообщение."""
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")


async def generate_html_files(message: types.Message, data: dict):
    # Создаем папки, если их нет
    individual_dir = Path("individual_ankets")
    ankets_dir = Path("ankets")
    images_dir = Path("../images")
    individual_dir.mkdir(exist_ok=True)
    ankets_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    # Генерируем случайный 6-значный ID
    random_id = random.randint(100000, 999999)
    chat_id = message.chat.id

    # Имя файлов
    filename = f"{chat_id}-{random_id}"
    individual_file = individual_dir / f"{filename}.html"
    ankets_file = ankets_dir / f"{filename}.html"

    # Получаем список фотографий
    photo_list = data.get("photo_list", [])
    first_photo_path = ""
    gallery_images_html = ""

    if photo_list:
        # Первая фотография для первого HTML
        first_photo_path = f"../images/{photo_list[0]}"

        # Генерируем галерею для второго HTML
        gallery_images = []
        for photo in photo_list:
            gallery_images.append(
                f'<img loading="lazy" src="../images/{photo}" alt="" width="1065" height="705">'
            )
        gallery_images_html = "\n".join(gallery_images)

    # Заполняем первый HTML файл (individual_ankets)
    template1 = """<div class="list-item__item js-list-item" data-name="ТУТ ИМЯ АНКЕТЫ" data-city="Очко" data-id="3844"> 
        <a href="/ankets/896-nastya-lisitsa.html" class="list-item__image" target="_blank" rel="noopener" data-top="">
            <img loading="lazy" width="140" height="210" alt="" src="ПУТЬ_К_ФОТО">
        </a>
        <div class="list-item__icons">
        </div>
    </a>
    <div class="list-item__desc">
        <div class="list-item__row">
            <strong>
                Возраст:
            </strong>
            <span>
                СЮДА ГОДА ПИСАТЬ
            </span>
        </div>
        <div class="list-item__row">
            <strong>
                Грудь:
            </strong>
            <span>
                РАЗМЕР ГРУДИ
            </span>
        </div>
        <div class="list-item__row">
            <strong>
                Вес:
            </strong>
            <span>
                СЮДА ВЕС
            </span>
        </div>
        <div class="list-item__row">
            <strong>
                Рост:
            </strong>
            <span>
                СЮДА РОСТ
            </span>
        </div>
        <div class="list-item__row list-item__row--full">
            <span class="list-item__cut tags">
                <a href="#"
                    class="cut_tag b-btn--small b-btn--blue disabled "
                    style="text-decoration: none; cursor: pointer;">
                    ФЕТИШИ
                </a>
            </span>
        </div>
    </div>
    <div class="list-item__title">
        <a href="/ankets/896-nastya-lisitsa.html">ТУТ ИМЯ АНКЕТЫ</a>
    </div>
    <div class="list-item__address">
        <div class="district">
            <a href="">
                ГОРОД АНКЕТЫ
            </a>
        </div>

    </div>

    <div class="list-item__buttons ">
        <button  class="b-btn b-btn--blue b-btn--small js-show-phone"
            onclick="showNotification('Телефон будет доступен после заказа');">
            <i class="icon-phone-white" aria-hidden="true"></i>
            <span>Показать телефон</span>
        </button>
        <button
            class="b-btn b-btn--blue b-btn--center b-btn--small js-show-tg"
            onclick="showNotification('Телеграмм будет доступен после заказа');">
            <i class="icon-telegram-white" aria-hidden="true"></i>
        </button>
        <button data-id="3844" rel="nofollow noopener"
            class="b-btn b-btn--blue b-btn--center b-btn--small js-show-wa"
            onclick="showNotification('WhatsApp будет доступен после заказа');">
            <i class="icon-whatsapp-white" aria-hidden="true"></i>
        </button>
    </div>

    <div id="notification" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); 
        background-color: rgba(0, 0, 0, 0.8); color: white; padding: 15px 25px; border-radius: 5px; z-index: 1000;">
    </div>

    <script>
    function showNotification(message) {
        const notification = document.getElementById('notification');
        notification.innerText = message;
        notification.style.display = 'block';

        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
    </script>

    <style>
    .b-btn {
        cursor: pointer;
        margin: 5px;
    }
    </style>

    <div class="list-item__price-list">
        <div class="list-item__price">

        </div>
    </div>
</div>
</div>"""

    filled_template1 = template1.replace("ТУТ ИМЯ АНКЕТЫ", data['name'])
    filled_template1 = filled_template1.replace("СЮДА ГОДА ПИСАТЬ", data['age'])
    filled_template1 = filled_template1.replace("РАЗМЕР ГРУДИ", data['boobs'])
    filled_template1 = filled_template1.replace("СЮДА ВЕС", data['weight'])
    filled_template1 = filled_template1.replace("СЮДА РОСТ", data['height'])
    filled_template1 = filled_template1.replace("ГОРОД АНКЕТЫ", data['city'])
    filled_template1 = filled_template1.replace("/ankets/896-nastya-lisitsa.html", f"/ankets/{filename}.html")
    filled_template1 = filled_template1.replace("ПУТЬ_К_ФОТО", first_photo_path if photo_list else "")

    with open(individual_file, "w", encoding="utf-8") as f:
        f.write(filled_template1)

    # Заполняем второй HTML файл (ankets)
    template2 = """<!DOCTYPE html>
<html lang="ru">

<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Элитная проститутка</title>


	<link rel="preload" href="themes/molvo/assets/fonts/hinted-Commissioner-Bold.woff2" as="font" type="font/woff2"
		crossorigin>
	<link rel="preload" href="themes/molvo/assets/fonts/hinted-Commissioner-ExtraBold.woff2" as="font" type="font/woff2"
		crossorigin>
	<link rel="preload" href="themes/molvo/assets/fonts/hinted-Commissioner-Regular.woff2" as="font" type="font/woff2"
		crossorigin>
	<link href="/css/app.css" rel="stylesheet">
	<link rel="stylesheet" href="/css/style.css">
	<link rel="manifest" href="themes/molvo/assets/images/site.webmanifest">
	<link rel="mask-icon" href="themes/molvo/assets/images/safari-pinned-tab.svg" color="#ff2103">
	<meta name="format-detection" content="telephone=no">
	<meta name="msapplication-TileColor" content="#ffffff">
	<meta name="theme-color" content="#ffffff">
	<meta name="csrf-token" content="X6zlFaSDOjOfcFhnlypTLmSN3lt5lSl39gE7ikEI">
	<meta name="exoclick-site-verification" content="c0ff7f96fde95f69a4f665bc0cc5d793">
	<meta name="enot" content="6541656433809NL0_nMLJUpT4wTtybeKcYi3JTegbE1mO">
	<meta name="recaptcha-key" id="recaptcha-key" content="6LchUeMqAAAAAD6QFmbqvkByVzzsTvFHQMLU5agU">
	<script
		type="text/javascript"> (function (m, e, t, r, i, k, a) { m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments) }; m[i].l = 1 * new Date(); for (var j = 0; j < document.scripts.length; j++) { if (document.scripts[j].src === r) { return; } } k = e.createElement(t), a = e.getElementsByTagName(t)[0], k.async = 1, k.src = r, a.parentNode.insertBefore(k, a) })(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym"); ym(92567495, "init", { clickmap: true, trackLinks: true, accurateTrackBounce: true }); </script>
	<noscript>
		<div><img src="https://mc.yandex.ru/watch/92567495" style="position:absolute; left:-9999px;" alt="" /></div>
	</noscript> <!-- /Yandex.Metrika counter -->
<link rel="icon" href="/favicon.png" type="image/png" />



	<link rel="stylesheet" href="https://cdn.plyr.io/3.6.8/plyr.css" />

</head>

<body>


	<div class="page-wrapper">
		<header class="header">
			<div class="header__inner">
				<div class="wrapper">
					<div class="header__search">
						<form class="search-panel" method="GET">
							<div class="header-right-group">
								<a href="/" class="header__logo">
									<img loading="lazy" src="/images/sweetsnights.svg"
										style="width: 130px; height: 40px; min-width: 130px"
										alt="Ashoo сайт интимных знакомств" height="38" width="130">
								</a>
								<div class="search-panel__box">
									<div class="search-panel__panel">
										<div class="search-panel__inner">
											<input type="text" inputmode="search" id="search-q"
												class="search-panel__input" aria-label="Поиск по сайту"
												placeholder="Имя, описание" name="q" data-empty="ru" value="">
											<button type="button" class="search-panel__close">
												<i class="icon-close-white" aria-hidden="true"></i>
												Закрыть
											</button>
											<button type="submit" class="search-panel__submit">Искать</button>
										</div>
									</div>


								</div>
							</div>

							<div class="header__dummy">
								<div class="header-topbar">
									<div class="wrapper">
										<nav class="header-topbar__menu">
											<ul>

												<li>
													<a href="/">Главная</a>
												</li>
												<li>
													<a href="/health .php.html">Health+</a>
												</li>
												<li>
													<a href="/location.html">Адрес</a>
												</li>
												<div class="header-topbar__geolocation">
													<button type="button" class="geolocation-box__trigger">
														<i class="icon-geolocation" aria-hidden="true"></i>
														<span>Москва</span>
													</button>
												</div>
												<style>
													.header-topbar__geolocation {
														margin-left: 60px;
													}
												</style>
											</ul>
										</nav>

									</div>
						</form>
		</header>


		<main class="main">
			<script type="application/ld+json">
	null
</script>
			<div class="wrapper">
				<ul class="pathway__list" itemscope itemtype="http://schema.org/BreadcrumbList">
				</ul>
				<article class="item">
					<header class="item-header">
						<h1 class="section__title" data-top="0">
							СЮДА ПОДСТАВИТЬ ИМЯ, СЮДА ВОЗРАСТ год - vip секс услуги
						</h1>

						<div class="item-header__panel ">
							<div class="item-contacts__container">
								<div class="item-contacts__part part-left">
								</div>

								<div class="item-contacts__part part-right">

									<button class="btn" id="orderButton">Оформить заказ</button>

									<div class="item-contacts__messengers">
										<button rel="nofollow noopener" data-id="896"
											class="b-btn b-btn--outline-blue js-show-tg item-contacts__item"
											onclick="if(window.fbq)fbq('track', 'Contact');ym(92567495,'reachGoal','STARTTELEGRAM', {URL: document.location.href});return true;">
											<i aria-hidden="true" class="icon-telegram-blue"></i>
											<span>Telegram</span>
										</button>
										<button data-id="896" rel="nofollow noopener"
											class="b-btn b-btn--outline-blue js-show-wa item-contacts__item"
											onclick="if(window.fbq)fbq('track', 'Contact');ym(92567495,'reachGoal','STARTWHATSAPP', {URL: document.location.href});return true;">
											<i aria-hidden="true" class="icon-whatsapp-blue"></i>
											<span>Whatsapp</span>
										</button>
									</div>
								</div>
							</div>
						</div>
					</header>

    <div class="item__panel">
        <div class="item__gallery">
            <div class="fotorama" data-nav="thumbs">
                ГАЛЕРЕЯ_ФОТО
            </div>
        </div>
    <div class="item__main">
							<div class="item-list__grid">
								<ul class="item-list">
									<li class="item-list__row">
										<div class="item-list__title">Город:</div>
										<div class="item-list__main" id="city">СЮДА ПОДСТАВИТЬ ГОРОД</div>
									</li>
									<li class="item-list__row">
										<div class="item-list__title">Возраст:</div>
										<div class="item-list__main" id="yo">СЮДА ПОДСТАВИТЬ СКОЛЬКО ГОДОВ</div>
									</li>
									<li class="item-list__row">
										<div class="item-list__title">Грудь:</div>
										<div class="item-list__main" id="breast">СЮДА РАЗМЕР ГРУДИН</div>
									</li>
									<li class="item-list__row">
										<div class="item-list__title">Вес:</div>
										<div class="item-list__main" id="weight">СЮДА ПОДСТАВИТЬ ВЕС</div>
									</li>
									<li class="item-list__row">
										<div class="item-list__title">Рост:</div>
										<div class="item-list__main" id="height">СЮДА ПОДСТАВИТЬ РОСТ</div>
									</li>
									<li class="item-list__row">
										<div class="item-list__title">Размер одежды:</div>
										<div class="item-list__main" id="clothing_size">СЮДА ПОДСТАВИТЬ РАЗМЕР ОДЕЖДЫ</div>
									</li>
									<li class="item-list__row">
										<div class="item-list__title">Размер обуви:</div>
										<div class="item-list__main" id="shoe_size">СЮДА ПОДСТАВИТЬ РАЗМЕР ОБУВИ</div>
									</li>
								</ul>




								</li>
								<li class="item-list__row">
									<div class="item-list__title">
										Теги:
									</div>
									<div class="item-list__main b__tags">
										<a href="" class="b-btn--small b-btn--blue is-starred tag-6">
											Индивидуалка
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											Анальный секс
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											МБР
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											Эскорт
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											Целуюсь
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											Апартаменты
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											Выезд
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											Есть подруга
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											GFE
										</a>
										<a href="" class="b-btn--small b-btn--blue ">
											С видео
										</a>
									</div>
								</li>
								</ul>
							</div>
							<div class="item-content">
								<p>
									Я стану твоей фавориткой❤)elite escort
									Ссылки на Инстаграм и телеграм канал в тексте к анкете
								</p>	
							</div>
						</div>
					</div>
					<div class="item-grid">
						<div class="item-grid__row item-grid__row--main">
							<section class="item-time__section">
								<div class="d-flex d-flex__fd_row d-flex__ai_c"
									style="justify-content: space-between; margin-bottom: 20px;">
									<h2 class="item__subtitle" style="margin: 0; line-height: normal;">
										Тариф
									</h2>
								</div>
								<div class="item-time__row">
									<h3 class="item-time__title">
										Днём
									</h3>
									<div class="item-time__grid">
										<div class="item-time__cell">
											<div class="item-time__item ">
												<div class="item-time__header">
													<div class="item-time__icon">
														<img loading="lazy" src="/themes/molvo/assets/images/sun.svg"
															width="50" height="50" alt="">
													</div>
													<div class="item-time__name">
														1 час
													</div>
												</div>
												<div class="item-time__list">
													<span>У меня</span>
													<strong>СЮДА ЦЕНА У МЕНЯ ЗА ЧАС ₽</strong>
												</div>
												<div class="item-time__list">
													<span>У тебя*</span>
													<strong>ЗДЕСЬ ЦЕНА У ТЕБЯ ЗА ЧАС ₽</strong>
												</div>
											</div>
										</div>
										<div class="item-time__cell">
											<div class="item-time__item ">
												<div class="item-time__header">
													<div class="item-time__icon">
														<img loading="lazy" src="/themes/molvo/assets/images/sun-2.svg"
															width="50" height="50" alt="">
													</div>
													<div class="item-time__name">
														2 часа
													</div>
												</div>
												<div class="item-time__list">
													<span>У меня</span>
													<strong>ЗДЕСЬ ЦЕНА У МЕНЯ ЗА 2 ЧАСА ₽</strong>
												</div>
												<div class="item-time__list">
													<span>У тебя*</span>
													<strong>ЗДЕСЬ ЦЕНА У ТЕБЯ ЗА 2 ЧАСА ₽</strong>
												</div>
											</div>
										</div>
									</div>
								</div>
								<div class="item-time__row">
									<h3 class="item-time__title">
										Ночью
									</h3>
									<div class="item-time__grid">
										<div class="item-time__cell">
											<div class="item-time__item item-time__item--dark">
												<div class="item-time__header">
													<div class="item-time__icon">
														<img loading="lazy" src="/themes/molvo/assets/images/moon.svg"
															width="50" height="50" alt="">
													</div>
													<div class="item-time__name">
														1 час
													</div>
												</div>
												<div class="item-time__list">
													<span>У меня</span>
													<strong>ЗДЕСЬ ЦЕНА ЗА ЧАС У МЕНЯ НОЧЬЮ ₽</strong>
												</div>
												<div class="item-time__list">
													<span>У тебя*</span>
													<strong>ЗДЕСЬ ЦЕНА У ТЕБЯ ЗА ЧАС НОЧЬЮ ₽</strong>
												</div>
											</div>
										</div>
										<div class="item-time__cell">
											<div class="item-time__item item-time__item--dark">
												<div class="item-time__header">
													<div class="item-time__icon">
														<img loading="lazy" src="/themes/molvo/assets/images/moon-2.svg"
															width="50" height="50" alt="">
													</div>
													<div class="item-time__name">
														Ночь
													</div>
												</div>
												<div class="item-time__list">
													<span>У меня</span>
													<strong>ЗДЕСЬ ЦЕНА У МЕНЯ ЗА НОЧЬ ₽</strong>
												</div>
												<div class="item-time__list">
													<span>У тебя*</span>
													<strong>ЗДЕСЬ ЦЕНА У ТЕБЯ ЗА НОЧЬ ₽</strong>
												</div>
											</div>
										</div>
									</div>
								</div>


							</section>
						</div>
						<section class="item-feature">

						</section>
						<section class="item-feature">
							<h2 class="item__subtitle">
								Предпочтения
							</h2>
							<div class="item-feature__grid">
								<div class="item-feature__cell">
									<div class="item-feature__title">
										Секс
									</div>
									<ul class="item-feature__list">
										<li>
											<a href="">Секс
												классический</a>
										</li>
										<li>
											<a href="">Секс анальный</a>

										</li>
										<li>
											<a href="">Секс
												групповой</a>

										</li>
										<li>
											<a href="">Секс
												лесбийский</a>

										</li>
										<li>
											<a href="">Семейной
												паре</a>
										</li>
										<li>
											<a href="">Минет в
												резинке</a>
										</li>
										<li>
											<a href="">Минет без резинки</a>
										</li>
										<li>
											<a href="">Минет
												глубокий</a>
										</li>
										<li>
											<a href="">Минет
												горловой</a>

										</li>
										<li>
											<a href="">Минет в
												машине</a>
										</li>
										<li>
											<a href="">Куннилингус</a>
										</li>
										<li>
											<a href="">Целуюсь</a>
										</li>
										<li>
											<a href="">Игрушки</a>

										</li>
										<li>
											<a href="">Окончание на
												грудь</a>
										</li>
										<li>
											<a href="">Окончание на
												лицо</a>
										</li>
										<li>
											<a href="">Окончание в
												рот</a>
											<div class="item-feature_desc">

											</div>
										</li>
										<li>
											<a href="poza-69/moskva">Поза 69</a>
										</li>
									</ul>
								</div>
								<div class="item-feature__cell">
									<div class="item-feature__title">
										Массаж
									</div>
									<ul class="item-feature__list">
										<li>
											<a href="">Массаж
												классический</a>
										</li>
										<li>
											<a href="">Массаж
												расслабляющий</a>
										</li>
										<li>
											<a href="">Массаж
												урологический</a>
										</li>
										<li>
											<a href="">Массаж
												эротический</a>
										</li>
										<li>
											<a href="">Массаж
												семейной паре</a>
										</li>
									</ul>
								</div>
								<div class="item-feature__cell">
									<div class="item-feature__title">
										Стриптиз
									</div>
									<ul class="item-feature__list">
										<li>
											<a href="">Стриптиз не
												профи</a>
										</li>
										<li>
											<a href="">Лесби
												откровенное</a>
										</li>
										<li>
											<a href="">Лесби-шоу
												легкое</a>
										</li>
									</ul>
								</div>
								<div class="item-feature__cell">
									<div class="item-feature__title">
										Экстрим
									</div>
									<ul class="item-feature__list">
										<li>
											<a href="">Страпон</a>

										</li>
										<li>
											<a href="">Анилингус
												клиенту</a>

										</li>
										<li>
											<a href="">Анилингус мне</a>
										</li>
										<li>
											<a href="">Золотой
												дождь клиенту</a>

										</li>
										<li>
											<a href="">Золотой дождь
												мне</a>
											<div class="item-feature_desc">
											</div>
										</li>
										<li>
											<a href="">Фистинг
												анальный клиенту</a>
											<div class="item-feature_desc">

											</div>
										</li>
										<li>
											<a href="">Фистинг
												анальный мне</a>
											<div class="#">

											</div>
										</li>
										<li>
											<a href="#">Фистинг
												классический</a>
											<div class="item-feature_desc">

											</div>
										</li>
										<li>
											<a href="#">Фингеринг</a>
										</li>
									</ul>
								</div>
								<div class="item-feature__cell">
									<div class="item-feature__title">
										Садо-мазо
									</div>
									<ul class="item-feature__list">
										<li>
											<a href="#">Госпожа</a>
										</li>
										<li>
											<a href="#">Доминирование</a>
										</li>
										<li>
											<a href="#">Рабыня</a>
											<div class="item-feature_desc">

											</div>
										</li>
										<li>
											<a href="#">Подчинение</a>
										</li>
										<li>
											<a href="#">Бондаж</a>
										</li>
										<li>
											<a href="#">Порка</a>
										</li>
										<li>
											<a href="#">Фетиш</a>
											>
										</li>
										<li>
											<a href="#">Трамплинг</a>
										</li>
										<li>
											<a href="#">Шибари</a>
										</li>
										<li>
											<a href="#">Фейсситтинг</a>
										</li>
										<li>
											<a href="#">Копро (выдача)</a>
											<div class="item-feature_desc">

											</div>
										</li>
									</ul>
								</div>
								<div class="item-feature__cell">
									<div class="item-feature__title">
										Разное
									</div>
									<ul class="item-feature__list">
										<li>
											<a href="#">GFE</a>
										</li>
										<li>
											<a href="#">Сопровождение</a>
										</li>
										<li>
											<a href="#">Ролевые игры</a>
										</li>
										<li>
											<a href="#">Фото/видео
												съемка</a>
										</li>
										<li>
											<a href="#">Готова к поездкам в
												другой город</a>
										</li>
										<li>
											<a href="#">Есть шенген</a>
										</li>
										<li>
											<a href="#">Есть
												загранпаспорт</a>
										</li>
										<li>
											<a href="#">Клизма</a>
										</li>
										<li>
											<a href="#">Пип-шоу</a>
										</li>
									</ul>
								</div>
								<div class="item-feature__cell">
									<div class="item-feature__title">
										Только у меня
									</div>
									<ul class="item-feature__list">
										<li>
											Самый лучший сервис и Гостеприимство на достойном уровне
										</li>
										<li>
											без силикона и Без пафоса
										</li>
										<li>
											PlayStation, кальян и
											Дорогие алкогольные напитки
										</li>
										<li>
											Парковка удобная и
											Бесплатная
										</li>
										<li>
											Без диспетчера
											Настоящая индивидуалка)) отвечаю на звонки сама)
										</li>
										<li>
											Свежие поперсы
										</li>
										<li>
											Любой каприз
											За ваши деньги)
										</li>
										<li>
											Бесплатное меню для моих гостей))
										</li>
										<li>
											Практикую экстремальный секс
										</li>
									</ul>
								</div>
								<div class="item-feature__sizer"></div>
							</div>
						</section>

					</div>
					<div class="item-grid__row item-grid__row--aside">
					</div>
			</div>
			</article>
	</div>




	<style>
		.modal-prepay_confirm {
			border-radius: 12px;
			color: #ffffff;
			padding: 8px;
			margin-top: 8px;
			cursor: pointer;
			min-width: 150px;
			text-align: center;
			justify-content: center;
			font-size: 14px;
		}

		.modal-prepay {
			min-width: 300px;
			max-width: 620px;
		}
	</style>

	</main>
	<div class="footer-info">
		<div class="wrapper">
			<table>
				<thead>
					<tr>
						<th>Сайт проституток</th>
						<th>Sweetnights это:</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>✅ Надежно</td>
						<td>Только настоящие проверенные анкеты и объявления</td>
					</tr>
					<tr>
						<td>✅ Удобно</td>
						<td>Большой выбор проституток на любой вкус и цену</td>
					</tr>
					<tr>
						<td>✅ Быстро</td>
						<td>Рядом с Вами обязательно найдётся</td>
					</tr>
					<tr>
						<td>✅ Безотказно</td>
						<td>Номера проституток указаны на сайте и они ждут вашего звонка</td>
					</tr>
					<tr>
						<td>✅ Круглосуточно</td>
						<td>Работаем по выходным и праздникам 24 часа в сутки</td>
					</tr>
				</tbody>
			</table>
			<hr />

		</div>
	</div>

	<div class="wrapper">
		<div class="footer__grid">
			<div class="footer__copyright">
				<a href="/" class="footer__logo">
					<img loading="lazy" src="../images/sweetsnights.svg" alt="Ashoo сайт интимных знакомств" height="38"
						width="134">
				</a>
				<p>&copy; 2021–2025, Sweetnights —
					проект, созданный для удобного поиска проституток, массажисток и эскорт-моделей по всей
					России.</p>
			</div>
			<div class="footer__menu">
				<ul>
					<li>
						<a href="/">Главная</a>
					</li>
					<li>
						<a href="o-proekte">О проекте</a>
					</li>
					<li>
						<a href="health">HEALTH+</a>

					</li>
				</ul>
				<ul>
					<li>
						<a href="polzovatelskoe-soglashenie-dlya-klientov">Пользовательское
							соглашение для клиентов</a>
					</li>
					<li>
						<a href="contacts">Контакты</a>
					</li>
				</ul>
			</div>
			<div class="footer__mark">
				<img loading="lazy" src="../images/logo.svg" alt="Сайт 18+" width="38" height="38">
			</div>
		</div>
	</div>
	</footer>
	<button id="b_scroller" type="button">
		<i class="icon-up" aria-hidden="true" title="Наверх"></i>
	</button>
	</div>





	</div>
	</div>





	<!DOCTYPE html>
	<html lang="ru">

	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Форма заказа</title>

	</head>

	<body>
		<div id="orderModal" class="modal">
			<div class="modal-content">
				<span class="close">×</span>
				<h1>Оформление заказа</h1>

				<label for="meetingDate">Дата встречи:</label>
				<input type="date" id="meetingDate" required>

				<label for="meetingTime">Время встречи:</label>
				<input type="time" id="meetingTime" required>

				<label for="meetingPlace">Место встречи:</label>
				<select id="meetingPlace" required>
					<option value="" disabled selected>Выберите место</option>
					<option value="У модели">У модели</option>
					<option value="У клиента">У клиента</option>
				</select>

				<label for="tariff">Тариф:</label>
				<select id="tariff" required>
					<option value="" disabled selected>Выберите тариф</option>
				</select>

				<label for="preferences">Выберите предпочтения:</label>
				<textarea id="preferences" rows="4" placeholder="Введите ваши предпочтения" required></textarea>

				<label for="contact">Контакт (Telegram/WhatsApp):</label>
				<input type="text" id="contact" placeholder="Telegram/WhatsApp" required>

				<a class="baton" href="#" id="linkOrder">Оформить</a>
			</div>

		</div>

		<script>

			document.getElementById('orderButton').onclick = function () {
				document.getElementById('orderModal').style.display = "block";
			}

			document.getElementsByClassName('close')[0].onclick = function () {
				document.getElementById('orderModal').style.display = "none";
			}

			window.onclick = function (event) {
				if (event.target == document.getElementById('orderModal')) {
					document.getElementById('orderModal').style.display = "none";
				}
			}

			const inputs = document.querySelectorAll('#orderModal input, #orderModal select');
			const linkOrder = document.getElementById('linkOrder');

			function checkInput() {
				const allFilled = Array.from(inputs).every(el => {
					return el.value && !(el.tagName === 'SELECT' && el.selectedIndex === 0);
				});
				linkOrder.classList.toggle('active', allFilled);
			}

			inputs.forEach(input => {
				input.addEventListener('change', checkInput);
				input.addEventListener('input', checkInput);
			});

			linkOrder.onclick = function (event) {
				event.preventDefault();

				const orderData = {
					date: document.getElementById("meetingDate").value,
					time: document.getElementById("meetingTime").value,
					place: document.getElementById("meetingPlace").value,
					tariff: document.getElementById("tariff").value,
					preferences: document.getElementById("preferences").value,
					contact: document.getElementById("contact").value,
					amount: document.getElementById("tariff").value
				};

				localStorage.setItem('orderData', JSON.stringify(orderData));


				window.location.href = '/1742043985-1.html';
			};
		</script>

		<script>

const allTariffs = [];

function loadTariffsData() {
	const dayItems = document.querySelectorAll('.item-time__row:not(.night) .item-time__item');
	const nightItems = document.querySelectorAll('.item-time__row.night .item-time__item');

	const processItems = (items, timeOfDay) => {
		items.forEach(item => {
			const name = item.querySelector('.item-time__name').textContent.trim();
			const lists = item.querySelectorAll('.item-time__list');

			if (lists.length === 2) {
				const priceMe = lists[0].querySelector('strong').textContent.trim();
				const priceYou = lists[1].querySelector('strong').textContent.trim();

				allTariffs.push({
					timeOfDay,
					duration: name,
					me: priceMe,
					you: priceYou
				});
			}
		});
	};

	processItems(dayItems, 'День');
	processItems(nightItems, 'Ночь');
}

function updateTariffOptions(place) {
	const tariffSelect = document.getElementById("tariff");
	tariffSelect.innerHTML = '<option value="" disabled selected>Выберите тариф</option>';

	allTariffs.forEach(tariff => {
		let price = '';
		let locationLabel = '';

		if (place === 'У модели') {
			price = tariff.me;
			locationLabel = 'У модели';
		} else if (place === 'У клиента') {
			price = tariff.you;
			locationLabel = 'У клиента';
		} else {
			return; 
		}

		if (price) {
			const option = document.createElement('option');
			option.value = price;
			option.textContent = `[${tariff.timeOfDay}] ${tariff.duration} — ${locationLabel} — ${price}₽`;
			tariffSelect.appendChild(option);
		}
	});
}

document.getElementById("meetingPlace").addEventListener('change', function () {
	updateTariffOptions(this.value);
	checkInput();
});

window.onload = function () {
	document.querySelectorAll('.item-time__title').forEach(title => {
		if (title.textContent.includes('Ночью')) {
			title.closest('.item-time__row').classList.add('night');
		}
	});

	loadTariffsData();
};


		</script>



		<link href="https://cdnjs.cloudflare.com/ajax/libs/fotorama/4.6.4/fotorama.css" rel="stylesheet">


		<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>


		<script src="https://cdnjs.cloudflare.com/ajax/libs/fotorama/4.6.4/fotorama.js"></script>

		<script>
			document.addEventListener('DOMContentLoaded', function () {

				$('.fotorama').fotorama({
					nav: 'thumbs',
					loop: true,
					autoplay: false
				});
			});
		</script>


	</body>

	</html>


</body>

<div id="contact-modal" style="
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  align-items: center;
  justify-content: center;
  z-index: 1000;
">
  <div style="
    background: white;
    padding: 20px 30px;
    border-radius: 10px;
    max-width: 300px;
    text-align: center;
  ">
    <p style="margin-bottom: 20px;">Будет доступен после заказа</p>
    <button onclick="document.getElementById('contact-modal').style.display='none';"
      style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
      Ок
    </button>
  </div>
</div>

<script>
  document.addEventListener('DOMContentLoaded', function () {
    const showModal = () => {
      const modal = document.getElementById('contact-modal');
      modal.style.display = 'flex'; // Показать
    };

    document.querySelectorAll('.js-show-tg, .js-show-wa').forEach(button => {
      button.addEventListener('click', function (event) {
        event.preventDefault(); // Отключаем стандартное поведение
        showModal();
      });
    });
  });
</script>

</html>"""

    filled_template2 = template2.replace("СЮДА ПОДСТАВИТЬ ИМЯ, СЮДА ВОЗРАСТ год", f"{data['name']}, {data['age']} год")
    filled_template2 = filled_template2.replace("СЮДА ПОДСТАВИТЬ ГОРОД", data['city'])
    filled_template2 = filled_template2.replace("СЮДА ПОДСТАВИТЬ СКОЛЬКО ГОДОВ", data['age'])
    filled_template2 = filled_template2.replace("СЮДА РАЗМЕР ГРУДИН", data['boobs'])
    filled_template2 = filled_template2.replace("СЮДА ПОДСТАВИТЬ ВЕС", data['weight'])
    filled_template2 = filled_template2.replace("СЮДА ПОДСТАВИТЬ РОСТ", data['height'])
    filled_template2 = filled_template2.replace("СЮДА ПОДСТАВИТЬ РАЗМЕР ОДЕЖДЫ", data['clothing_size'])
    filled_template2 = filled_template2.replace("СЮДА ПОДСТАВИТЬ РАЗМЕР ОБУВИ", data['shoe_size'])
    filled_template2 = filled_template2.replace("ГАЛЕРЕЯ_ФОТО",
                                                gallery_images_html if photo_list else '<img loading="lazy" src="../images/1.svg" alt="" width="1065" height="705">')

    # Заменяем цены
    filled_template2 = filled_template2.replace("СЮДА ЦЕНА У МЕНЯ ЗА ЧАС ₽", data['h1_i_price'])
    filled_template2 = filled_template2.replace("ЗДЕСЬ ЦЕНА У ТЕБЯ ЗА ЧАС ₽", data['h1_you_price'])
    filled_template2 = filled_template2.replace("ЗДЕСЬ ЦЕНА У МЕНЯ ЗА 2 ЧАСА ₽", data['h2_i_price'])
    filled_template2 = filled_template2.replace("ЗДЕСЬ ЦЕНА У ТЕБЯ ЗА 2 ЧАСА ₽", data['h2_you_price'])
    filled_template2 = filled_template2.replace("ЗДЕСЬ ЦЕНА ЗА ЧАС У МЕНЯ НОЧЬЮ ₽", data['night_h1_i_price'])
    filled_template2 = filled_template2.replace("ЗДЕСЬ ЦЕНА У ТЕБЯ ЗА ЧАС НОЧЬЮ ₽", data['night_h1_you_price'])
    filled_template2 = filled_template2.replace("ЗДЕСЬ ЦЕНА У МЕНЯ ЗА НОЧЬ ₽", data['full_night_i_price'])
    filled_template2 = filled_template2.replace("ЗДЕСЬ ЦЕНА У ТЕБЯ ЗА НОЧЬ ₽", data['full_night_you_price'])

    with open(ankets_file, "w", encoding="utf-8") as f:
        f.write(filled_template2)

    return filename


@dp.callback_query_handler(text="sozd_ank")
async def sozd_ank_call(callback: types.CallbackQuery, state: FSMContext):
    msg = await bot.send_message(
        callback.from_user.id, text="Начинаем создание анкеты.\nВведите имя:"
    )
    await Anketa.name.set()
    await callback.answer()  # Отвечаем на callback, чтобы убрать "часики"
    await state.update_data(last_bot_message_id=msg.message_id)  # Сохраняем ID последнего сообщения бота


@dp.message_handler(state=Anketa.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Введите возраст:")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.age.set()


@dp.message_handler(state=Anketa.age)
async def get_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите возраст числом:")
        return

    await state.update_data(age=message.text)

    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Введите размер груди:")
    await state.update_data(last_bot_message_id=msg.message_id)

    await Anketa.boobs.set()


@dp.message_handler(state=Anketa.boobs)
async def get_boobs(message: types.Message, state: FSMContext):
    await state.update_data(boobs=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Введите вес (кг):")
    await state.update_data(last_bot_message_id=msg.message_id)

    await Anketa.weight.set()


@dp.message_handler(state=Anketa.weight)
async def get_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Введите рост (см):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.height.set()


@dp.message_handler(state=Anketa.height)
async def get_height(message: types.Message, state: FSMContext):
    await state.update_data(height=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Введите город:")
    await state.update_data(last_bot_message_id=msg.message_id)

    await Anketa.city.set()


@dp.message_handler(state=Anketa.city)
async def get_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Введите размер одежды:")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.clothing_size.set()


@dp.message_handler(state=Anketa.clothing_size)
async def get_clothing_size(message: types.Message, state: FSMContext):
    await state.update_data(clothing_size=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Введите размер обуви:")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.shoe_size.set()


@dp.message_handler(state=Anketa.shoe_size)
async def get_shoe_size(message: types.Message, state: FSMContext):
    await state.update_data(shoe_size=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Цена за час (у меня):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.h1_i_price.set()


@dp.message_handler(state=Anketa.h1_i_price)
async def get_h1_i_price(message: types.Message, state: FSMContext):
    await state.update_data(h1_i_price=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Цена за час (у тебя):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.h1_you_price.set()


@dp.message_handler(state=Anketa.h1_you_price)
async def get_h1_you_price(message: types.Message, state: FSMContext):
    await state.update_data(h1_you_price=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Цена за 2 часа (у меня):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.h2_i_price.set()


@dp.message_handler(state=Anketa.h2_i_price)
async def get_h2_i_price(message: types.Message, state: FSMContext):
    await state.update_data(h2_i_price=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Цена за 2 часа (у тебя):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.h2_you_price.set()


@dp.message_handler(state=Anketa.h2_you_price)
async def get_h2_you_price(message: types.Message, state: FSMContext):
    await state.update_data(h2_you_price=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Цена за 1 час ночью (у меня):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.night_h1_i_price.set()


@dp.message_handler(state=Anketa.night_h1_i_price)
async def get_night_h1_i_price(message: types.Message, state: FSMContext):
    await state.update_data(night_h1_i_price=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Цена за 1 час ночью (у тебя):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.night_h1_you_price.set()


@dp.message_handler(state=Anketa.night_h1_you_price)
async def get_night_h1_you_price(message: types.Message, state: FSMContext):
    await state.update_data(night_h1_you_price=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Цена за полную ночь (у меня):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.full_night_i_price.set()


@dp.message_handler(state=Anketa.full_night_i_price)
async def get_full_night_i_price(message: types.Message, state: FSMContext):
    await state.update_data(full_night_i_price=message.text)
    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Отправляем следующий вопрос и запоминаем ID сообщения
    msg = await message.answer("Цена за полную ночь (у тебя):")
    await state.update_data(last_bot_message_id=msg.message_id)
    await Anketa.full_night_you_price.set()


@dp.message_handler(state=Anketa.full_night_you_price)
async def get_full_night_you_price(message: types.Message, state: FSMContext):
    await state.update_data(full_night_you_price=message.text)

    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    # Создаем клавиатуру с кнопкой "Готово"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Готово")
    keyboard.add(button)

    # Запрашиваем фото
    msg = await message.answer(
        "Отправьте свои фотографии. Когда закончите, нажмите кнопку 'Готово'.",
        reply_markup=keyboard,
    )
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.update_data(
        photo_list=[]
    )  # Инициализируем список для хранения имен файлов
    await Anketa.photo.set()


@dp.message_handler(content_types=types.ContentType.PHOTO, state=Anketa.photo)
async def process_photo(message: types.Message, state: FSMContext):
    """Обрабатываем фотографии."""
    chat_id = message.chat.id
    photo = message.photo[-1]  # Берем фото самого высокого разрешения
    file_id = photo.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path

    # Генерируем случайное шестизначное число для имени файла
    random_number = random.randint(100000, 999999)
    filename = f"{chat_id}_{random_number}.jpg"
    filepath = os.path.join(IMAGE_DIR, filename)

    try:
        # Скачиваем фото
        await bot.download_file(file_path, filepath)

        # Получаем текущий список фото из state и добавляем новое
        data = await state.get_data()
        photo_list = data.get("photo_list", [])
        photo_list.append(filename)
        await state.update_data(photo_list=photo_list)

        await message.answer(f"Фотография сохранена")

    except Exception as e:
        await message.answer(f"Ошибка при скачивании и сохранении фотографии: {e}")

    # Удаляем сообщение пользователя с фото
    await delete_message(message)


@dp.message_handler(state=Anketa.photo, text="Готово")
async def finish_photo(message: types.Message, state: FSMContext):
    """Заканчиваем прием фотографий и выводим анкету с фото."""

    # Удаляем сообщение пользователя
    await delete_message(message)

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    if "last_bot_message_id" in data:
        try:
            await bot.delete_message(message.chat.id, data["last_bot_message_id"])
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    data = await state.get_data()

    # Генерируем HTML файлы
    filename = await generate_html_files(message, data)

    # Формируем сообщение с информацией об анкете
    anketa_text = "<b>Ваша анкета:</b>\n"
    anketa_text += f"Имя: {data['name']}\n"
    anketa_text += f"Возраст: {data['age']}\n"
    anketa_text += f"Размер груди: {data['boobs']}\n"
    anketa_text += f"Вес: {data['weight']}\n"
    anketa_text += f"Рост: {data['height']}\n"
    anketa_text += f"Город: {data['city']}\n"
    anketa_text += f"Размер одежды: {data['clothing_size']}\n"
    anketa_text += f"Размер обуви: {data['shoe_size']}\n"
    anketa_text += f"Цена за час (у меня): {data['h1_i_price']}\n"
    anketa_text += f"Цена за час (у тебя): {data['h1_you_price']}\n"
    anketa_text += f"Цена за 2 часа (у меня): {data['h2_i_price']}\n"
    anketa_text += f"Цена за 2 часа (у тебя): {data['h2_you_price']}\n"
    anketa_text += f"Цена за 1 час ночью (у меня): {data['night_h1_i_price']}\n"
    anketa_text += f"Цена за 1 час ночью (у тебя): {data['night_h1_you_price']}\n"
    anketa_text += f"Цена за полную ночь (у меня): {data['full_night_i_price']}\n"
    anketa_text += f"Цена за полную ночь (у тебя): {data['full_night_you_price']}\n"

    # Отправляем анкету
    await message.answer(anketa_text, parse_mode="HTML")

    # Получаем список фотографий из state
    photo_list = data.get("photo_list", [])

    # Отправляем фотографии
    if photo_list:
        media = types.MediaGroup()
        for filename in photo_list:
            filepath = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(filepath):
                media.attach_photo(types.InputFile(filepath))
            else:
                print(f"Файл {filepath} не найден!")
        try:
            await bot.send_media_group(message.chat.id, media=media)
        except Exception as e:
            print(f"Ошибка при отправке группы фото: {e}")

    await bot.send_message(message.from_user.id,
                           text="Анкета загружена",
                           reply_markup=keyboardBack())
    await state.finish()


@dp.callback_query_handler(text='lc')
async def lc_call(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    user_id = callback.from_user.id
    user = USERS.get(USERS.user_id == callback.from_user.id)
    date = datetime.fromtimestamp(user.timestamp)
    current_date = datetime.fromtimestamp(time.time())
    days_in_team = (current_date - date).days
    count = [0,0,0]
    tag = user.tag
    for log in PAY.select():
        if log.user_id == user_id:
            count[2] += log.count
            tm = detect_time(log.timestamp)
            if tm == 0:
                count[0] += log.count
                count[1] += log.count
            if tm == 1:
                count[1] += log.count
    if user.teacher:
        text = f'''
👤Профиль: <i>{user_id}</i>| <b>Учитель</b>
📆Количество дней в команде: <i>{days_in_team}</i>
👛Имя в выплатах: {tag}
    
💳 Сумма профитов:
└ За день: <b>{count[0]} RUB</b>
└ За месяц: <b>{count[1]} RUB</b> 
└ За все время: <b>{count[2]} RUB</b>

'''
    else:
        if user.teach == '1':
            text = f'''
👤Профиль: <i>{user_id}</i>
📆Количество дней в команде: <i>{days_in_team}</i>
👨‍🏫Наставник: <i>В ожидании...</i>
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: <b>{count[0]} RUB</b>
└ За месяц: <b>{count[1]} RUB</b> 
└ За все время: <b>{count[2]} RUB</b>

            '''
        elif user.teach not in ('0', '2'):
            text = f'''
👤Профиль: <i>{user_id}</i>
📆Количество дней в команде: <i>{days_in_team}</i>
👨‍🏫Наставник: <i>{USERS.get(USERS.username == user.teach).tag}</i>
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: <b>{count[0]} RUB</b>
└ За месяц: <b>{count[1]} RUB</b> 
└ За все время: <b>{count[2]} RUB</b>

            '''
        else:
            text = f'''
👤Профиль: <i>{user_id}</i>
📆Количество дней в команде: <i>{days_in_team}</i>
👨‍🏫Наставник: <i>Не выбран</i>
👛Имя в выплатах: {tag}

💳 Сумма профитов:
└ За день: <b>{count[0]} RUB</b>
└ За месяц: <b>{count[1]} RUB</b> 
└ За все время: <b>{count[2]} RUB</b>

            '''

    last_message_db[callback.from_user.id] = await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboardBack(),parse_mode="HTML")
    await callback.answer()


@dp.callback_query_handler(text='add_none')
async def add_profit(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    if callback.from_user.id in admins:
        temp_user_db[callback.from_user.id] = ['', '', None]
        last_message_db[callback.from_user.id] = await bot.send_message(chat_id=callback.from_user.id, text=f'Введите сумму профита', reply_markup=keyboardCancel())
        await UserStates.ADMIN_QUESTION1.set()
        await callback.answer()


@dp.callback_query_handler(text='addprofit')
async def add_profit(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    if callback.from_user.id in admins:
        temp_user_db[callback.from_user.id] = ['', '', '']
        last_message_db[callback.from_user.id] = await bot.send_message(chat_id=callback.from_user.id, text=f'Введите сумму профита', reply_markup=keyboardCancel())
        await UserStates.ADMIN_QUESTION1.set()
        await callback.answer()

#q0
@dp.message_handler(state=UserStates.ADMIN_QUESTION0)
async def processQUESTION0(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        if message.text.isdigit():
            temp_user_db[message.from_user.id][2] = int(message.text)
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Введите сумму профита',
                                   reply_markup=keyboardCancel())
            await UserStates.ADMIN_QUESTION1.set()
        else:
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Процент должен быть числом')

#q1
@dp.message_handler(state=UserStates.ADMIN_QUESTION1)
async def processQUESTION1(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        if temp_user_db[message.from_user.id][2] == None:
            temp_user_db[message.from_user.id][0] = int(message.text)
            last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id,
                                                                           text='Введите тег воркера без #',
                                                                           reply_markup=keyboardCancel())
            await UserStates.ADMIN_QUESTION2.set()
        else:
            if message.text.isdigit():
                temp_user_db[message.from_user.id][0] = int(message.text)
                last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id,
                                                                               text='Введите юзернейм воркера без @',
                                                                               reply_markup=keyboardCancel())
                await UserStates.ADMIN_QUESTION2.set()
            else:
                last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id,
                                                                               text='Сумма должна быть числом')


#q2
@dp.message_handler(state=UserStates.ADMIN_QUESTION2)
async def processQUESTION2(message: types.Message,state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    if message.text in ('Отмена❌', '/start'):
        await show_main_menu(message)
        await state.finish()
    else:
        if temp_user_db[message.from_user.id][2] == None:
            add_log('#'+message.text.replace('#', ''), temp_user_db[message.from_user.id][0], True)
            await message.answer('Готово!')
            await show_main_menu(message)
            await state.finish()
        else:
            try:
                user = USERS.get(USERS.username == message.text)
                user_id = user.user_id
                tag = user.tag
                temp_user_db[message.from_user.id][1] = user_id
                await final_profit(temp_user_db[message.from_user.id], tag, message.from_user.id)
                last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Профит успешно добавлен')
                await state.finish()
                await show_main_menu(message)
            except Exception as e:
                print(e)
                last_message_db[message.from_user.id] = await bot.send_message(chat_id=message.from_user.id, text='Такого пользователя нет в базе.\nВведите юзернейм', reply_markup=keyboardCancel())

async def final_profit(temp_user_db, tag, user_id):
    count = 0
    for log in PAY.select():
        if log.user_id == temp_user_db[1]:
            count += 1
    if count >= 3:
        edit_user(user_id=temp_user_db[1], teach='2')

    add_log(temp_user_db[1], temp_user_db[0])
    await bot.send_message(chat_id=user_id, text=f'''💋 Успешный платеж!

💴 Сумма платежа: {temp_user_db[0]} RUB

👑Воркер: {tag}
Доля воркера: {temp_user_db[0]} RUB''')


async def can_ban_members(chat_id, user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id, user_id)
        return chat_member.can_restrict_members
    except:
        return False


@dp.message_handler(commands="ban")
async def cmd_ban(message: types.Message):
    if await can_ban_members(message.chat.id, message.from_user.id):
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
        await bot.kick_chat_member(chat_id=message.chat.id, user_id=user_id)
        await message.reply(f'Пользователь забанен!', reply_markup=keyboardUnban(user_id))

@dp.message_handler(commands='mute')
async def mute_user(message: types.Message):
    if await can_ban_members(message.chat.id, message.from_user.id):
        try:
            seconds = int(message.get_args())
            if seconds <= 30:
                await message.reply("Некорректные параметры. Кол-во секунд не должно быть меньше 30")
                return
        except:
            await message.reply("Некорректные параметры. Используйте /mute <количество секунд>")
            return

        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id

        try:
            until_date = datetime.now() + timedelta(seconds=seconds)
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                until_date=until_date,
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
            await message.reply(f'Пользователь замучен на {seconds} секунд!', reply_markup=keyboardUnmute(user_id))
        except Exception as e:
            print(e)

@dp.callback_query_handler(Text(startswith='unban_'))
async def unban_user(callback: types.CallbackQuery):
    if await can_ban_members(callback.message.chat.id, callback.from_user.id):
        user_id = int(callback.data.split('_')[1])
        chat_id = callback.message.chat.id
        try:
            await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
            await bot.send_message(chat_id=chat_id, text='Пользователь разбанен')
            try:
                await callback.message.delete()
            except:
                pass
        except Exception as e:
            print(e)

@dp.callback_query_handler(Text(startswith='unmute_'))
async def unmute_user(callback: types.CallbackQuery):
    if await can_ban_members(callback.message.chat.id, callback.from_user.id):
        user_id = int(callback.data.split('_')[1])
        chat_id = callback.message.chat.id
        try:
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            await bot.send_message(chat_id=chat_id, text='Пользователь размучен✅')
            try:
                await callback.message.delete()
            except:
                pass
        except Exception as e:
            print(e)


@dp.message_handler(text='Отмена❌')
async def back(message: types.Message, state: FSMContext):
    try:
        await last_message_db[message.from_user.id].delete()
    except:
        pass
    await state.finish()
    await show_main_menu(message)

@dp.message_handler(content_types = ['new_chat_members', 'left_chat_member'])
async def delete(message):
    await bot.delete_message(message.chat.id, message.message_id)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling())
