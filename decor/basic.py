import random

from db.db import BotDB


def show_form(name, age, city, text):
    return f'{name}\n{age}\n{city}\n{text}'


def crop_list(text):
    return text and ' '.join(word for word in text.split()[:-1])

"""
def get_random_form(list_of_forms):
    form = list_of_forms[random.randint(0, len(list_of_forms) - 1)]
    a = form
    return [show_form(a[2], a[3], a[4], a[5]), BotDB.get_photo_id(a[1])]

def caption(user_id):
    form = db.db.BotDB.get_form(user_id)
    a = form[0]
    return show_form(a[2], a[3], a[4], a[5])


def list_of_forms(user_id):
    form = BotDB.get_form(user_id)
    a = form[0]
    return BotDB.find_forms(user_id, a[7], a[4], a[3])


def rand(user_id):
    form = get_random_form(list_of_forms(user_id))
    return form

def get_random_form(user_id):
    form = BotDB.get_form(user_id)
    a = form[0]
    list_of_forms = BotDB.find_forms(user_id, a[7], a[4], a[3])
    form = list_of_forms[random.randint(0, len(list_of_forms) - 1)]
    a = form

    form = BotDB.get_form(user_id)
    a = form[0]
    return BotDB.find_forms(user_id, a[7], a[4], a[3])

    return [show_form(a[2], a[3], a[4], a[5]), BotDB.get_photo_id(a[1])]

"""