from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove
import text

main_menu = [
    [KeyboardButton(text=text.main_menu_today_note)],
    [KeyboardButton(text=text.main_menu_archive),
     KeyboardButton(text=text.main_menu_settings)]
]
main_menu = ReplyKeyboardMarkup(keyboard=main_menu, resize_keyboard=True)

write_menu = [
    [KeyboardButton(text=text.write_menu_hint)],
    [KeyboardButton(text=text.any_menu_back)]
]
write_menu = ReplyKeyboardMarkup(keyboard=write_menu, resize_keyboard=True)

menu_back = [
    [KeyboardButton(text=text.any_menu_back)]
]
menu_back = ReplyKeyboardMarkup(keyboard=menu_back, resize_keyboard=True)

archive_menu = [
    [KeyboardButton(text=text.archive_menu_find_date)],
    [KeyboardButton(text=text.archive_menu_period)],
    [KeyboardButton(text=text.archive_menu_download_all)],
    [KeyboardButton(text=text.any_menu_back)]
]
archive_menu = ReplyKeyboardMarkup(keyboard=archive_menu, resize_keyboard=True)

settings_menu = [
    [KeyboardButton(text=text.settings_menu_how_to_use)],
    [KeyboardButton(text=text.settings_menu_bot_about),
     KeyboardButton(text=text.settings_menu_pay)],
    [KeyboardButton(text=text.settings_menu_hide_mode),
     KeyboardButton(text=text.settings_menu_notif)],
    [KeyboardButton(text=text.settings_menu_timezone),
     KeyboardButton(text=text.settings_menu_delete_all)],
    [KeyboardButton(text=text.any_menu_back)]
]
settings_menu = ReplyKeyboardMarkup(keyboard=settings_menu, resize_keyboard=True)

settings_menu_no_ads = [
    [KeyboardButton(text=text.settings_menu_bot_about),
     KeyboardButton(text=text.settings_menu_how_to_use)],
    [KeyboardButton(text=text.settings_menu_hide_mode),
     KeyboardButton(text=text.settings_menu_notif)],
    [KeyboardButton(text=text.settings_menu_timezone),
     KeyboardButton(text=text.settings_menu_delete_all)],
    [KeyboardButton(text=text.any_menu_back)]
]
settings_menu_no_ads = ReplyKeyboardMarkup(keyboard=settings_menu_no_ads, resize_keyboard=True)

confirm_menu = [
    [KeyboardButton(text=text.yes),
     KeyboardButton(text=text.no)]
]
confirm_menu = ReplyKeyboardMarkup(keyboard=confirm_menu, resize_keyboard=True)

empty_note_menu = [
    [KeyboardButton(text=text.write_menu_hint),
     KeyboardButton(text=text.any_menu_back)]
]
empty_note_menu = ReplyKeyboardMarkup(keyboard=empty_note_menu, resize_keyboard=True)

action_note_menu = [
    [KeyboardButton(text=text.write_menu_hint),
     KeyboardButton(text=text.write_edit_note)],
    [KeyboardButton(text=text.write_delete_note),
     KeyboardButton(text=text.any_menu_back)]
]
action_note_menu = ReplyKeyboardMarkup(keyboard=action_note_menu, resize_keyboard=True)

hide_mode_off_menu = [
    [KeyboardButton(text=text.turn_on)],
     [KeyboardButton(text=text.any_menu_back)]
]
hide_mode_off_menu = ReplyKeyboardMarkup(keyboard=hide_mode_off_menu, resize_keyboard=True)

hide_mode_on_menu = [
    [KeyboardButton(text=text.tyrn_off)],
     [KeyboardButton(text=text.any_menu_back)]
]
hide_mode_on_menu = ReplyKeyboardMarkup(keyboard=hide_mode_on_menu, resize_keyboard=True)

next_menu = [
    [KeyboardButton(text=text.chose_period_next)],
     [KeyboardButton(text=text.chose_period_exit)]
]
next_menu = ReplyKeyboardMarkup(keyboard=next_menu, resize_keyboard=True)

conf = [
    [InlineKeyboardButton(text=text.yes, callback_data=text.yes)],
    [InlineKeyboardButton(text=text.no, callback_data=text.no)]
]
conf = InlineKeyboardMarkup(inline_keyboard=conf)

chose_action = [
    [InlineKeyboardButton(text=text.archive_menu_download_all, callback_data=text.archive_menu_download_all)],
    [InlineKeyboardButton(text=text.settings_menu_delete_all, callback_data=text.settings_menu_delete_all)]
]
chose_action = InlineKeyboardMarkup(inline_keyboard=chose_action)

menu_technique = [
    [InlineKeyboardButton(text=text.teqn_1, callback_data='teqn_1')],
    [InlineKeyboardButton(text=text.teqn_2, callback_data='teqn_2')],
    [InlineKeyboardButton(text=text.teqn_3, callback_data='teqn_3')],
    [InlineKeyboardButton(text=text.teqn_4, callback_data='teqn_4')]
]
menu_technique = InlineKeyboardMarkup(inline_keyboard=menu_technique)

menu_technique_back = [
    [InlineKeyboardButton(text=text.teqn_back, callback_data=text.teqn_back)]
]
menu_technique_back = InlineKeyboardMarkup(inline_keyboard=menu_technique_back)
