import datetime
import re

import pytz
import timezonefinder
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from geopy.geocoders import Nominatim
from payments import create

import payments
from db import Cursor
from states import My_States
from aiogram.utils.keyboard import InlineKeyboardBuilder

import kb
import text
import config
from user import User

router = Router()


@router.message(StateFilter(None), Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    with Cursor() as cur:

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                ads INTEGER,
                time_zone TEXT,
                time_reminder TEXT,
                hide_mode INTEGER,
                last_executive_date TEXT
            )
            """
        )

        if len(cur.execute(
                "SELECT user_id FROM users WHERE user_id = '{0}'".format(msg.from_user.id)).fetchall()) == 0:
            cur.execute(
                f'INSERT INTO users (user_id, ads, time_zone, time_reminder, hide_mode, last_executive_date) '
                f'VALUES (?, ?, ?, ?, ?, ?)',
                (msg.from_user.id, 1, 'Europe/Moscow', '-', 0, '-'))
            cur.execute(
                """CREATE TABLE IF NOT EXISTS '{0}'(date TEXT NOT NULL UNIQUE, note TEXT)""".format(msg.from_user.id))
            await msg.answer(text.greet)
            await to_change_timezone(msg, state)


async def to_change_timezone(msg, state):
    await state.set_state(My_States.timezone_waiting)
    await msg.answer(text.change_timezone_meet, reply_markup=kb.menu_back)


async def to_settings(msg, state):
    await state.set_state(My_States.settings_state)
    if User.check_ads(msg.from_user.id):
        await msg.answer(User.current_settings(msg.from_user.id), reply_markup=kb.settings_menu)
    else:
        await msg.answer(User.current_settings(msg.from_user.id), reply_markup=kb.settings_menu_no_ads)


async def to_main(msg, state):
    await state.clear()
    await msg.answer(text.main_menu_meet, reply_markup=kb.main_menu)


@router.callback_query(lambda c: 'check' in c.data)
async def check_handler(callback: types.CallbackQuery):
    if payments.check(callback.data.split('_')[-1]):
        await User.make_sub(callback.from_user.id)
        await callback.bot.edit_message_text(text.payment_done, callback.from_user.id, callback.message.message_id)
    else:
        await callback.bot.send_message(callback.from_user.id, text.payment_wrong)


@router.callback_query(lambda c: c.data == text.teqn_back)
async def back_handler(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(text.hint, callback.from_user.id, callback.message.message_id,
                                         reply_markup=kb.menu_technique)


@router.callback_query(lambda c: 'teqn' in c.data)
async def teqn_handler(callback: types.CallbackQuery):
    number = callback.data.split('_')[-1]
    output = ''
    if number == '1':
        output = text.teqn_1_text
    elif number == '2':
        output = text.teqn_2_text
    elif number == '3':
        output = text.teqn_3_text
    elif number == '4':
        output = text.teqn_4_text
    await callback.bot.edit_message_text(output, callback.from_user.id, callback.message.message_id,
                                         reply_markup=kb.menu_technique_back)


@router.message(My_States.timezone_waiting)
async def func(msg: Message, state: FSMContext):
    tf = timezonefinder.TimezoneFinder()
    if msg.text is not None:
        if msg.text == text.any_menu_back:
            await to_settings(msg, state)
        else:
            try:
                geolocator = Nominatim(user_agent=config.MAP_TOKEN)
                location = geolocator.geocode(msg.text)
                if location is not None:
                    timezone_str = tf.certain_timezone_at(lat=location.latitude, lng=location.longitude)
                    await User.rewrite_timezone(msg.from_user.id, timezone_str)
                    await msg.answer(text.change_timezone_done)
                    await to_settings(msg, state)
                else:
                    await msg.answer(text.change_timezone_wrong)
            except Exception:
                await msg.answer(text.lose_conn)
    elif msg.location is not None:
        timezone_str = tf.certain_timezone_at(lat=msg.location.latitude, lng=msg.location.longitude)
        await User.rewrite_timezone(msg.from_user.id, timezone_str)
        await msg.answer(text.change_timezone_done)
        await to_settings(msg, state)
    else:
        await msg.answer(text.change_timezone_wrong)


async def to_change_notif(msg, state):
    await state.set_state(My_States.notif_waiting)
    await msg.answer(text.change_notif_meet, reply_markup=kb.menu_back)


async def to_delete_all(msg, state):
    await state.set_state(My_States.delete_all_confirm_waitnig)
    await msg.answer(text.delete_all_meet, reply_markup=kb.confirm_menu)


@router.message(My_States.delete_all_confirm_waitnig)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.yes:
        await User.delete_all(msg.from_user.id)
        await msg.answer(text.delete_all_done)
        await to_settings(msg, state)
    elif msg.text == text.no:
        await to_settings(msg, state)
    else:
        await msg.answer(text.wrong_comm)


@router.message(My_States.notif_waiting)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.any_menu_back:
        await to_settings(msg, state)
    else:
        forma = "%H%M"

        try:
            res = bool(datetime.datetime.strptime(msg.text, forma))
        except ValueError:
            res = False

        if res:
            await User.rewrite_notif(msg.from_user.id, msg.text)
            await msg.answer(text.change_notif_done)
            await to_settings(msg, state)
        else:
            await msg.answer(text.change_notif_wrong_format)


@router.message(My_States.settings_state)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.settings_menu_bot_about:
        await msg.answer(text.bot_about)
    elif msg.text == text.settings_menu_how_to_use:
        await msg.answer(text.how_to_use)
    elif msg.text == text.settings_menu_timezone:
        await to_change_timezone(msg, state)
    elif msg.text == text.settings_menu_notif:
        await to_change_notif(msg, state)
    elif msg.text == text.settings_menu_hide_mode:
        await to_change_hide_mode(msg, state)
    elif msg.text == text.settings_menu_delete_all:
        await to_delete_all(msg, state)
    elif msg.text == text.any_menu_back:
        await to_main(msg, state)
    elif msg.text == text.settings_menu_pay:
        await msg.answer('Подписка пока недоступна🙇‍♀️')
        """
        payment_url, payment_id = create(config.PRICE, msg.from_user.id, text.description)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text=text.pay_button,
            url=payment_url
        ))
        builder.add(types.InlineKeyboardButton(
            text=text.chek_payment,
            callback_data=f'check_{msg.from_user.id}_{payment_id}'
        ))
        builder.adjust(1)
        await msg.answer(text=text.sub_over, reply_markup=builder.as_markup())
        """
    else:
        await msg.answer(text.wrong_comm)


async def to_change_hide_mode(msg, state):
    await state.set_state(My_States.waiting_to_change_hide_mode)
    if User.check_hide_mode(msg.from_user.id) == 1:
        await msg.answer('...', reply_markup=kb.hide_mode_on_menu)
    else:
        await msg.answer('...', reply_markup=kb.hide_mode_off_menu)


@router.message(My_States.waiting_to_change_hide_mode)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.turn_on:
        await User.change_hide_mode(msg.from_user.id, 1)
        await to_settings(msg, state)
    elif msg.text == text.tyrn_off:
        await User.change_hide_mode(msg.from_user.id, 0)
        await to_settings(msg, state)
    elif msg.text == text.any_menu_back:
        await to_settings(msg, state)
    else:
        await msg.answer(text.wrong_comm)


async def to_archive(msg, state):
    await state.set_state(My_States.archive_state)
    await msg.answer(text.archive_menu_meet, reply_markup=kb.archive_menu)


async def show_note(msg, state, date_str):
    note = User.get_note_by_date(msg.from_user.id, date_str)
    if note is False:
        await msg.answer(text.empty_note, reply_markup=kb.empty_note_menu)
        await state.set_state(My_States.waiting_note_empty)
    else:
        if User.check_hide_mode(msg.from_user.id) == 1:
            await msg.answer(text='||' + escape_markdown(note) + '||', parse_mode='MarkdownV2',
                             reply_markup=kb.action_note_menu)
            await state.set_state(My_States.waiting_note_not_empty)
        else:
            await msg.answer(note, reply_markup=kb.action_note_menu)
            await state.set_state(My_States.waiting_note_not_empty)
    await msg.answer(text.write_menu_meet)


def escape_markdown(text: str, version: int = 2, entity_type: str = None) -> str:
    """
    Helper function to escape telegram markup symbols.

    Args:
        text (:obj:`str`): The text.
        version (:obj:`int` | :obj:`str`): Use to specify the version of telegrams Markdown.
            Either ``1`` or ``2``. Defaults to ``1``.
        entity_type (:obj:`str`, optional): For the entity types ``PRE``, ``CODE`` and the link
            part of ``TEXT_LINKS``, only certain characters need to be escaped in ``MarkdownV2``.
            See the official API documentation for details. Only valid in combination with
            ``version=2``, will be ignored else.
    """
    if int(version) == 1:
        escape_chars = r'_*`['
    elif int(version) == 2:
        if entity_type in ['pre', 'code']:
            escape_chars = r'\`'
        elif entity_type == 'text_link':
            escape_chars = r'\)'
        else:
            escape_chars = r'_*[]()~`>#+-=|{}.!'
    else:
        raise ValueError('Markdown version must be either 1 or 2!')

    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


@router.message(My_States.waiting_note_not_empty)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.write_menu_hint:
        await msg.answer(text.hint, reply_markup=kb.menu_technique)
    elif msg.text == text.any_menu_back:
        await to_main(msg, state)
    elif msg.text == text.write_delete_note:
        await delete_note(msg, state)
    elif msg.text == text.write_edit_note:
        await edit_note(msg, state)
    else:
        await User.add_to_note(msg.from_user.id, msg.text, False)
        await msg.answer(text.write_menu_done)
        if User.check_hide_mode(msg.from_user.id) == 1:
            await msg.delete()


async def delete_note(msg, state):
    await state.set_state(My_States.waiting_confirm_delete_note)
    await msg.answer(text.get_confirm, reply_markup=kb.confirm_menu)


async def edit_note(msg, state):
    await msg.answer(text.edit_note_meet, reply_markup=kb.menu_back)
    await state.set_state(My_States.waiting_note_to_edit)


@router.message(My_States.waiting_note_to_edit)
async def func(msg: Message, state: FSMContext):
    if msg.text is not None:
        if msg.text == text.any_menu_back:
            await state.set_state(My_States.waiting_note_not_empty)
            await msg.answer(text.write_menu_meet, reply_markup=kb.action_note_menu)
        else:
            await User.rewrite_note(msg.from_user.id, msg.text)
            await msg.answer(text.edit_note_done, reply_markup=kb.action_note_menu)
            await state.set_state(My_States.waiting_note_not_empty)
            if User.check_hide_mode(msg.from_user.id) == 1:
                await msg.delete()
    else:
        await msg.answer(text.wrong_comm)


@router.message(My_States.waiting_confirm_delete_note)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.yes:
        await User.delete_note(msg.from_user.id)
        await state.set_state(My_States.waiting_note_empty)
        await msg.answer(text.delete_note_done, reply_markup=kb.empty_note_menu)
    elif msg.text == text.no:
        await state.set_state(My_States.waiting_note_not_empty)
        await msg.answer(text.write_menu_meet, reply_markup=kb.action_note_menu)
    else:
        await msg.answer(text.wrong_comm)


@router.message(My_States.waiting_note_empty)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.write_menu_hint:
        await msg.answer(text.hint, reply_markup=kb.menu_technique)
    elif msg.text == text.any_menu_back:
        await to_main(msg, state)
    else:
        await User.add_to_note(msg.from_user.id, msg.text, True)
        await state.set_state(My_States.waiting_note_not_empty)
        await msg.answer(text.write_menu_done, reply_markup=kb.action_note_menu)
        if User.check_hide_mode(msg.from_user.id) == 1:
            await msg.delete()


@router.message(StateFilter(None))
async def func(msg: Message, state: FSMContext):
    if msg.text == text.main_menu_today_note:
        with Cursor() as cur:
            timezone_str = \
                cur.execute("SELECT time_zone FROM users WHERE user_id = '{0}'".format(msg.from_user.id)).fetchall()[0]
            date_str = datetime.datetime.now(pytz.timezone(timezone_str[0])).strftime('%d%m%y')
        await show_note(msg, state, date_str)
    elif msg.text == text.main_menu_archive:
        await to_archive(msg, state)
    elif msg.text == text.main_menu_settings:
        await to_settings(msg, state)
    else:
        await msg.answer(text.wrong_comm)


async def to_find_note_by_date(msg, state):
    await state.set_state(My_States.waiting_date_to_find)
    await msg.answer(text.find_date_meet, reply_markup=kb.menu_back)


@router.message(My_States.waiting_date_to_find)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.any_menu_back:
        await to_archive(msg, state)
    else:
        forma = "%d%m%y"

        try:
            res = bool(datetime.datetime.strptime(msg.text, forma))
        except ValueError:
            res = False

        if res:
            await show_note(msg, state, msg.text)
        else:
            await msg.answer(text.find_date_wrong_format)


async def to_chose_period(msg, state):
    await state.set_state(My_States.waiting_date_to_start)
    await msg.answer(text.chose_period_meet, reply_markup=kb.menu_back)


def period_shower(msg, state):
    contin = True
    while contin:
        next_date = datetime.datetime.strptime(User.get_last_exec_date(msg.from_user.id)[0],
                                               '%d%m%y') + datetime.timedelta(hours=24)
        next_date_str = next_date.strftime('%d%m%y')
        note = User.get_note_by_date(msg.from_user.id, next_date_str)
        if note is False:
            if next_date > datetime.datetime.now() + datetime.timedelta(hours=25):
                return False
        else:
            return note


@router.message(My_States.waiting_date_to_start)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.any_menu_back:
        await to_archive(msg, state)
    else:
        forma = "%d%m%y"
        try:
            res = bool(datetime.datetime.strptime(msg.text, forma))
        except ValueError:
            res = False
        if res:
            note = User.get_note_by_date(msg.from_user.id, msg.text)
            if note is False:
                con = period_shower(msg, state)
                if con is False:
                    await msg.answer(text.there_is_no_notes)
                    await to_archive(msg, state)
                else:
                    await show_note_with_date(msg, con)
                    await state.set_state(My_States.next_note_waiting)
            else:
                await show_note_with_date(msg, note)
                await state.set_state(My_States.next_note_waiting)
        else:
            await msg.answer(text.find_date_wrong_format)


@router.message(My_States.next_note_waiting)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.chose_period_exit:
        await to_archive(msg, state)
    elif msg.text == text.chose_period_next:
        com = period_shower(msg, state)
        if com is False:
            await msg.answer(text.there_is_no_notes)
            await to_archive(msg, state)
        else:
            await show_note_with_date(msg, com)
    else:
        await msg.answer(text.wrong_comm)


async def show_note_with_date(msg, note):
    date_str = (User.get_last_exec_date(msg.from_user.id))[0]
    final_note = date_str[0:2] + '.' + date_str[2:4] + '.20' + date_str[4:6] + '\n' + note
    if User.check_hide_mode(msg.from_user.id) == 1:
        await msg.answer(text='||' + escape_markdown(final_note) + '||', parse_mode='MarkdownV2',
                         reply_markup=kb.next_menu)
    else:
        await msg.answer(final_note, reply_markup=kb.next_menu)


@router.message(My_States.archive_state)
async def func(msg: Message, state: FSMContext):
    if msg.text == text.archive_menu_find_date:
        await to_find_note_by_date(msg, state)
    elif msg.text == text.archive_menu_period:
        await to_chose_period(msg, state)
    elif msg.text == text.archive_menu_download_all:
        try:
            await User.make_csv(msg.from_user.id)
            await msg.answer_document(
                document=FSInputFile(r'/root/user_xl/{0}.xlsx'.format(str(msg.from_user.id))),
                caption=text.download_all_done)
        except:
            await msg.answer(text.lose_conn)
    elif msg.text == text.any_menu_back:
        await to_main(msg, state)
    else:
        await msg.answer(text.wrong_comm)
