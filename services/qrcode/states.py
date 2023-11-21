from aiogram.dispatcher.filters.state import State, StatesGroup


class Wait(StatesGroup):
    qrcode = State()

    matchbot = State()
