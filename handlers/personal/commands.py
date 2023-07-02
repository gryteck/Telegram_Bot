from src.imp import *

BotDB = BotDB()


@dp.message_handler(commands="info", state="*")
async def info(message: types.Message):
    await bot.send_photo(photo=open(f"photos/info.png", "rb"), chat_id=message.from_user.id,
                         caption=t.info, reply_markup=kb.back())
    await message.answer("Мы в "+'<a href="https://t.me/asiaparty">телеграм</a>', parse_mode="HTML")


@dp.message_handler(commands="admin", state="*")
async def admin(message: types.Message):
    id = message.from_user.id
    if id in admins:
        await message.answer(t.admin_menu, reply_markup=kb.key_1234())
        await Wait.admin_menu.set()
    else:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(commands="restart", state="*")
async def restart(message: types.Message):
    if message.from_user.id not in admins:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()
        return
    BotDB.drop()
    BotDB.add_ban(supp_id)
    BotDB.ban_user(supp_id)
    await message.reply("Рестартнуто")


@dp.message_handler(commands="start", state="*")
async def form_start(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not BotDB.user_exists(id):
        await state.update_data(count=1, liked_id=id)
        await message.answer(t.set_gender, reply_markup=kb.key_gender())
        await Wait.choosing_gender.set()
    else:
        f = BotDB.get_form(id)
        await bot.send_photo(photo=f['photo'], chat_id=id, caption=b.cap(f))
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(commands="my_profile", state="*")
async def my_profile(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if not BotDB.user_exists(id):
        await state.update_data(count=1, liked_id=id)
        await message.answer(t.set_gender, reply_markup=kb.key_gender())
        await Wait.choosing_gender.set()
    else:
        f = await BotDB.get_form(id)
        await bot.send_photo(photo=f['photo'], chat_id=id, caption=f['text'])
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await Wait.my_form_answer.set()
