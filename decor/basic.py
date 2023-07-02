import random


def show_form(name, age, text):
    if text != "":
        return f'{name}, {age} - {text}'
    else:
        return f'{name}, {age}'


def crop_list(text):
    return text and ' '.join(word for word in text.split()[:-1])


def cap(a: dict):
    if a['text'] == '':
        return f"{a['name']}, {a['age']}"
    else:
        return f"{a['name']}, {a['age']}, {a['text']}"


def ak(text: str):
    link = "t.me/asiaparty"
    k = f"<a href=\"{link}\">{text}</a>"
    return k
