from aiogram.dispatcher.filters.state import State, StatesGroup


class Wait(StatesGroup):
    choosing_gender = State()
    choosing_interest = State()
    name = State()
    age = State()
    city = State()
    text = State()
    photo = State()
    menu_answer = State()
    my_form_answer = State()
    change_text = State()
    change_photo = State()
    delete_confirm = State()
    form_reaction = State()
    match_status = State()
    like_list = State()
    like = State()
    like_reaction = State()
