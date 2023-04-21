from aiogram import Bot, Dispatcher, executor, types


def key_123():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3"]
    return keyboard.add(*buttons)


def key_reactions():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["❤️", "👎", "Вернуться назад"]
    return keyboard.add(*buttons)


def key_1234():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3", "4"]
    return keyboard.add(*buttons)


def key_gender():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Парень", "Девушка"]
    return keyboard.add(*buttons)


def key_interest():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Парни", "Девушки"]
    return keyboard.add(*buttons)


def key_empty():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    return keyboard.add("Оставить пустым")


def key_yesno():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Да", "Нет"]
    return keyboard.add(*buttons)
