from aiogram import types


def key_123():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3"]
    return keyboard.add(*buttons)


def react():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Оцени",
                                         one_time_keyboard=True)
    buttons = ["❤️", "👎", "🚫", "Вернуться назад"]
    return keyboard.add(*buttons)


def key_1234():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3", "4"]
    return keyboard.row(*buttons)


def key_gender():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="укажите пол...")
    buttons = ["Парень", "Девушка"]
    return keyboard.add(*buttons)


def key_interest():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Кто вам интересен?")
    buttons = ["Парни", "Девушки"]
    return keyboard.add(*buttons)


def key_empty():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Опишите себя")
    return keyboard.add("Оставить пустым")


def key_yesno():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Да", "Нет"]
    return keyboard.add(*buttons)


def cont():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                         input_field_placeholder="продолжить?")
    return keyboard.add("Продолжить")


def back():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                         input_field_placeholder="вернуться")
    return keyboard.add("Вернуться назад")


def ban():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["✅", "❌", "⁉️", "↩️"]
    return keyboard.row(*buttons)


def match(id):
    button_url = f'tg://user?id={id}'
    markup = types.InlineKeyboardMarkup()
    return markup.add(types.InlineKeyboardButton(text="Написать человечку", url=button_url))
