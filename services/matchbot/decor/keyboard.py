from aiogram import types

from db.schemas import SUser


def admin(f: SUser):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Refresh ↩️", callback_data=f"refresh:{f.id}")
    if f.banned:
        button2 = types.InlineKeyboardButton(text="Enable ✅", callback_data=f"enable:{f.id}")
    else:
        button2 = types.InlineKeyboardButton(text="Disable ❌", callback_data=f"disable:{f.id}")
    button3 = types.InlineKeyboardButton(text="Warn ⁉️", callback_data=f"warn:{f.id}")
    return keyboard.row(button1, button2, button3)


def admin_warn(f: SUser):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Picture", callback_data=f"image:{f.id}")
    button2 = types.InlineKeyboardButton(text="Bio", callback_data=f"bio:{f.id}")
    button3 = types.InlineKeyboardButton(text="Back", callback_data=f"back:{f.id}")
    return keyboard.row(button1, button2, button3)


def key_123():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ("1", "2", "3")
    return keyboard.add(*buttons)


def react():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Оцени",
                                         one_time_keyboard=True)
    buttons = ("❤️", "🚫", "👎", "💤")
    return keyboard.row(*buttons)


def custom(text: str) -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [text]
    return keyboard.add(*buttons)


def key_1234():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ("1", "2", "3", "4")
    return keyboard.row(*buttons)


def gender():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                         input_field_placeholder="Укажи свой пол...")
    buttons = ("Парень", "Девушка")
    return keyboard.add(*buttons)


def interest():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                         input_field_placeholder="Кого ищешь...")
    buttons = ("Парни", "Девушки")
    return keyboard.add(*buttons)


def keep_empty():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Опиши себя...")
    return keyboard.add("Оставить пустым")


def yes_no():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ("Да", "Нет")
    return keyboard.add(*buttons)


def cont():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                         input_field_placeholder="Продолжить?")
    return keyboard.add("Продолжить")


def back():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return keyboard.add("Вернуться назад")


def ban():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="id...")
    buttons = ("✅", "❌", "⁉️", "↩️")
    return keyboard.row(*buttons)


def match(id):
    if type(id) == int:
        button_url = f'tg://user?id={id}'
    else:
        button_url = f't.me/{id}'
    markup = types.InlineKeyboardMarkup()
    return markup.add(types.InlineKeyboardButton(text="Написать человечку", url=button_url))


def rules():
    button_url = 't.me/asiaparty'
    markup = types.InlineKeyboardMarkup()
    return markup.add(types.InlineKeyboardButton(text="Правила посещения", url=button_url))

