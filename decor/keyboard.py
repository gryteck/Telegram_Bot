from aiogram import Bot, Dispatcher, executor, types


def key_123():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3"]
    return keyboard.add(*buttons)


def key_reactions():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Как вам человечек?")
    buttons = ["❤️", "👎", "Вернуться назад"]
    return keyboard.add(*buttons)


def key_1234():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3", "4"]
    return keyboard.add(*buttons)


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
                                         input_field_placeholder="продолжить смотреть тех, кому вы понравились?")
    return keyboard.add("Продолжить")


def back():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                         input_field_placeholder="вернуться")
    return keyboard.add("Вернуться назад")
# def inl_reactions():
