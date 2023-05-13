from aiogram.dispatcher.filters.state import State, StatesGroup


class Wait(StatesGroup):
    choosing_gender = State()
    choosing_interest = State()
    name = State()
    age = State()
    city = State()
    text = State()
    photo = State()

    upd_gender = State()
    upd_interest = State()
    upd_name = State()
    upd_age = State()
    upd_city = State()
    upd_text = State()
    upd_photo = State()

    menu_answer = State()
    instructions = State()

    my_form_answer = State()
    change_text = State()
    change_photo = State()
    delete_confirm = State()

    form_reaction = State()
    match_status = State()
    like_list = State()

    claim = State()
    claim_liked = State()
    claim_text = State()
    claim_text_liked = State()

    admin_menu = State()
    admin_ban_list = State()
    get_form_by_id = State()
    get_ban_list = State()
    get_form_by_username = State()
    like = State()
    like_reaction = State()
