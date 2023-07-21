from aiogram.dispatcher.filters.state import State, StatesGroup


class Wait(StatesGroup):
    set_gender = State()
    set_interest = State()
    set_name = State()
    set_age = State()
    set_text = State()
    set_photo = State()

    menu_answer = State()
    instructions = State()

    my_form_answer = State()
    change_text = State()
    change_photo = State()
    delete_confirm = State()

    form_reaction = State()

    claim = State()
    claim_text = State()

    admin_menu = State()
    admin_ban_list = State()
    get_form_by_id = State()
    get_ban_list = State()
    get_form_by_username = State()

    get_photo = State()
