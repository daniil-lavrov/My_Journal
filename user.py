import asyncio
import sqlite3
import datetime
import re

import openpyxl as openpyxl
import pytz
from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile
from db import Cursor
from states import My_States

import kb
import text


class User:

    @staticmethod
    async def rewrite_timezone(user_id, new_timezone_str):
        with Cursor() as cur:
            cur.execute("UPDATE users SET time_zone = '{0}' WHERE user_id = '{1}'".format(new_timezone_str, user_id))

    @staticmethod
    async def change_hide_mode(user_id, var):
        with Cursor() as cur:
            cur.execute("UPDATE users SET hide_mode = '{0}' WHERE user_id = '{1}'".format(var, user_id))

    @staticmethod
    def check_hide_mode(user_id):
        with Cursor() as cur:
            hide_mode_int = \
                (cur.execute("SELECT hide_mode FROM users WHERE user_id = '{0}'".format(user_id)).fetchall())[0]
            return hide_mode_int[0]

    @staticmethod
    def current_settings(user_id, timezone_str=None, reminder_time_str=None):
        with Cursor() as cur:
            timezone_str = \
            (cur.execute("SELECT time_zone FROM users WHERE user_id = '{0}'".format(user_id)).fetchall())[0]
            reminder_time_str = \
            (cur.execute("SELECT time_reminder FROM users WHERE user_id = '{0}'".format(user_id)).fetchall())[0]
            ads = \
                ((cur.execute("SELECT ads FROM users WHERE user_id = '{0}'".format(user_id)).fetchall())[0])[0]
        hide_mode_str = ''
        if User.check_hide_mode(user_id) == 1:
            hide_mode_str = text.hide_mode_on
        else:
            hide_mode_str = text.hide_mode_off
        if ads == 1:
            ads_status = ''
        else:
            ads_status = '💎Активна подписка'
        current_settings_str = (
                    'Текущие настройки:' + '\n' + '🕐Часовой пояс: ' + timezone_str[0] + '\n' + '🔔Время напоминания: ' +
                    (reminder_time_str[0])[0:2] + ' ' + (reminder_time_str[0])[2:4] + '\n' + hide_mode_str + '\n' +
                    ads_status)
        return current_settings_str

    @staticmethod
    def get_last_exec_date(user_id):
        with Cursor() as cur:
            last_ex_date = cur.execute("SELECT last_executive_date FROM users WHERE user_id = '{0}'".format(user_id)).fetchall()[0]
            return last_ex_date

    @staticmethod
    def get_note_by_date(user_id, date_str):
        with Cursor() as cur:
            cur.execute("UPDATE users SET last_executive_date = '{0}' WHERE user_id = '{1}'".format(date_str, user_id))
            if len(cur.execute(
                    "SELECT note FROM '{0}' WHERE date = '{1}'".format(str(user_id), date_str)).fetchall()) == 0:
                return False
            else:
                note = (cur.execute(
                    "SELECT note FROM '{0}' WHERE date = '{1}'".format(str(user_id), date_str)).fetchall())[0]
                return note[0]

    @staticmethod
    async def make_csv(user_id):
        with Cursor() as cur:
            book = openpyxl.Workbook()
            sheet = book.active
            cur.execute("SELECT * FROM '{0}'".format(user_id))
            results = cur.fetchall()
            i = 0
            for row in results:
                i += 1
                j = 1
                for col in row:
                    cell = sheet.cell(row=i, column=j)
                    cell.value = col
                    j += 1

            book.save(r'/root/user_xl/{0}.xlsx'.format(str(user_id)))

    @staticmethod
    async def rewrite_notif(user_id, new_notif_str):
        with Cursor() as cur:
            cur.execute("UPDATE users SET time_reminder = '{0}' WHERE user_id = '{1}'".format(new_notif_str, user_id))

    @staticmethod
    async def delete_all(user_id):
        with Cursor() as cur:
            cur.execute("DELETE FROM '{0}'".format(user_id))

    @staticmethod
    async def rewrite_note(user_id, new_note):
        with Cursor() as cur:
            exec_date = (cur.execute("SELECT last_executive_date FROM users WHERE user_id = '{0}'".format(str(user_id)))
                         .fetchall())[0]
            if len(cur.execute("SELECT * FROM '{0}' WHERE date = '{1}'".format(user_id, exec_date[0])).fetchall()) == 0:
                cur.execute(
                    "INSERT INTO '{0}' (date, note) VALUES ('{1}', '{2}')".format(user_id, exec_date[0], ''))
            cur.execute("UPDATE '{0}' SET note = '{1}' WHERE date = '{2}'".format(user_id, new_note, exec_date[0]))

    @staticmethod
    async def add_to_note(user_id, note, empty):
        with Cursor() as cur:
            exec_date = (cur.execute("SELECT last_executive_date FROM users WHERE user_id = '{0}'".format(str(user_id)))
                         .fetchall())[0]
            try:
                curr_note = (cur.execute("SELECT note FROM '{0}' WHERE date = '{1}'".format(str(user_id), exec_date[0]))
                             .fetchall())[0]
            except:
                curr_note = ['']
        if empty:
            new_note = curr_note[0] + note
        else:
            new_note = curr_note[0] + '\n' + note
        await User.rewrite_note(user_id, new_note)

    @staticmethod
    async def delete_note(user_id):
        with Cursor() as cur:
            exec_date = (cur.execute("SELECT last_executive_date FROM users WHERE user_id = '{0}'".format(str(user_id)))
                         .fetchall())[0]
            if len(cur.execute("SELECT * FROM '{0}' WHERE date = '{1}'".format(user_id, exec_date[0])).fetchall()) == 0:
                cur.execute(
                    "INSERT INTO '{0}' (date, note) VALUES ('{1}', '{2}')".format(user_id, exec_date[0], ''))
            cur.execute("DELETE FROM '{0}' WHERE  date = '{1}'".format(user_id, exec_date[0]))

    @staticmethod
    def check_ads(user_id):
        with Cursor() as cur:
            ads = cur.execute(
                "SELECT ads FROM users WHERE user_id = '{0}'".format(user_id)).fetchone()[0]
            if ads == 1:
                return True
            else:
                return False

    @staticmethod
    async def make_sub(user_id):
        with Cursor() as cur:
            cur.execute('''UPDATE users SET ads = 0 WHERE user_id = "{0}"'''.format(user_id))


