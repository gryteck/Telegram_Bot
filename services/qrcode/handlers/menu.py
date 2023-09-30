from aiogram.utils import exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext

from config import dp, bot, supp_id, br_photo
from states import Wait

import decor.text as t
import decor.keyboard as kb

from db.schema import db

@dp.message_handler(state=Wait.qrcode)
async def qrcode(message: types.Message, state: FSMContext):
    await message.answer("Yaaaaay")
    await Wait.qrcode.set()

@dp.message_handler(state=Wait.matchbot)
async def qrcode(message: types.Message, state: FSMContext):
    return await Wait.matchbot.set()
