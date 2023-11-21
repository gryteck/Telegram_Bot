from asyncio import sleep

import decor.keyboard as kb
import decor.text as t
from aiogram import types
from aiogram.dispatcher import FSMContext
from config import dp, bot, admins
from db.schema import db
from states import Wait


@dp.message_handler(commands="qrcode", state="*")
async def command_qrcode(message: types.Message, state: FSMContext):
    await get_qrcode(message, state, "qrcode")

@dp.message_handler(commands="qr_admin", state="*")
async def qr_admin(message: types.Message):
    await message.answer("кидай фотку")
    await Wait.qr_admin.set()