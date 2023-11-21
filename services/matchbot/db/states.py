class State:
    def __get__(self, instance, owner):
        return f'{owner.__name__}.{self.name}'

    def __set_name__(self, owner, name):
        self.name = name


class Wait:
    start = State()

    finish = State()

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
    cont = State()

    claim = State()
    claim_text = State()

    admin = State()

    get_photo = State()