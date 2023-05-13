import random

from db.db import BotDB

BotDB = BotDB()


def show_form(name, age, text):
    if text != "":
        return f'{name}, {age} - {text}'
    else:
        return f'{name}, {age}'


def crop_list(text):
    return text and ' '.join(word for word in text.split()[:-1])


def cap(user_id):
    a = BotDB.get_form(user_id)[0]
    return show_form(a[2], a[3], a[5])


def ph(id):
    a = BotDB.get_form(id)[0]
    return a[4]


def get_random_form(id):
    a = BotDB.get_form(id)[0]
    list_of_forms = BotDB.find_forms(id, a[7], a[3])
    a = list_of_forms[random.randint(0, len(list_of_forms) - 1)]
    return [show_form(a[2], a[3], a[5]), a[1]]


def ak(text):
    link = "t.me/asiaparty"
    k = f"<a href=\"{link}\">{text}</a>"
    return k
