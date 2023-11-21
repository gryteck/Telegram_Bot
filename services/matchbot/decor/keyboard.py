from aiogram import types


def start():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Получить QR код", "Начать знакомства"]
    return keyboard.add(*buttons)


def key_123():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3"]
    return keyboard.add(*buttons)


def react():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Оцени",
                                         one_time_keyboard=True)
    buttons = ["❤️", "🚫", "👎", "💤"]
    return keyboard.row(*buttons)


def custom(text: str) -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [text]
    return keyboard.add(*buttons)


def key_1234():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3", "4"]
    return keyboard.row(*buttons)


def gender():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                         input_field_placeholder="Укажи свой пол...")
    buttons = ["Парень", "Девушка"]
    return keyboard.add(*buttons)


def interest():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                         input_field_placeholder="Кого ищешь...")
    buttons = ["Парни", "Девушки"]
    return keyboard.add(*buttons)


def keep_empty():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Опиши себя...")
    return keyboard.add("Оставить пустым")


def yes_no():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Да", "Нет"]
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
    buttons = ["✅", "❌", "⁉️", "↩️"]
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


def qr_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Что дальше?")
    buttons = ["Начать знакомства", "Изменить данные"]
    return keyboard.row(*buttons)
