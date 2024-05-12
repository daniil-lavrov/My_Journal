from aiogram.fsm.state import StatesGroup, State

class My_States(StatesGroup):
    today_note_state = State
    archive_state = State()
    settings_state = State()
    timezone_waiting = State()
    notif_waiting = State()
    delete_all_confirm_waitnig = State()
    waiting_note_empty = State()
    waiting_note_not_empty = State()
    waiting_confirm_delete_note = State()
    waiting_note_to_edit = State()
    waiting_to_change_hide_mode = State()
    waiting_date_to_find = State()
    next_note_waiting = State()
    waiting_date_to_start = State()