from aiogram.dispatcher.filters.state import State, StatesGroup


class Wait(StatesGroup):
    start = State()

    my_form_answer = State()
    set_gender = State()
    set_interest = State()
    set_name = State()
    set_age = State()
    set_text = State()
    set_photo = State()
    change_text = State()
    change_photo = State()
    delete_confirm = State()

    menu_answer = State()
    instructions = State()




    form_reaction = State()

    claim = State()
    claim_text = State()

    admin_menu = State()
    admin_ban_list = State()
    admin_form_by_id = State()
    admin_promo_check = State()
    admin_promo_new = State()

    get_photo = State()
    get_link = State()

    qrcode = State()
    qr_gender = State()
    qr_name = State()
    qr_age = State()
    qr_admin = State()
