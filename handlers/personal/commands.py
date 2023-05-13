from src.imp import *

BotDB = BotDB()


@dp.message_handler(commands="try", state="*")
async def tr(message: types.Message):
    b.get_random_form(message.from_user.id)


@dp.message_handler(commands="info", state="*")
async def info(message: types.Message):
    await bot.send_photo(photo=open(f"photos/info.png", "rb"), chat_id=message.from_user.id,
                         caption=t.info, reply_markup=k.back())
    await message.answer("Мы в "+'<a href="https://t.me/asiaparty">телеграм</a>', parse_mode="HTML")
    await Wait.like_list.set()


@dp.message_handler(commands="admin", state="*")
async def admin(message: types.Message):
    id = message.from_user.id
    if id in admins:
        await message.answer(t.admin_menu, reply_markup=k.key_1234())
        await Wait.admin_menu.set()
    else:
        await message.answer("Данная функция вам недоступна")
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()


@dp.message_handler(commands="like", state="*")
async def like(message: types.Message, state: FSMContext):
    id = message.from_user.id
    while len(BotDB.get_user_liked(id).split()) != 1:
        liked_str = str(BotDB.get_user_liked(message.from_user.id))
        liked_id = liked_str.split()[-1]
        if BotDB.form_exists(liked_id): break
        BotDB.update_liked(id, b.crop_list(liked_str))
    liked_str = str(BotDB.get_user_liked(id))
    if len(BotDB.get_user_liked(id).split()) == 1:
        await message.answer(t.like_list_end)
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        liked_id = liked_str.split()[-1]
        await state.update_data(liked_id=liked_id)
        await message.answer(t.like_list, reply_markup=k.react())
        await bot.send_photo(photo=b.ph(liked_id), chat_id=id, caption=b.cap(liked_id))
        await Wait.like_list.set()


@dp.message_handler(commands="res", state="*")
async def restart(message: types.Message):
    BotDB.drop()
    BotDB.add_ban(supp_id)
    BotDB.ban_user(supp_id)
    await message.reply("Рестартнуто")


@dp.message_handler(commands="start", state="*")
async def form_start(message: types.Message):
    id = message.from_user.id
    if not BotDB.user_exists(id):
        await message.answer(t.hello_text)
        BotDB.add_user(id)
        BotDB.add_ban(id)
    if BotDB.form_exists(id):
        await bot.send_photo(photo=b.ph(id), chat_id=id, caption=b.cap(id))
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        await message.answer(t.set_gender, reply_markup=k.key_gender())
        await Wait.choosing_gender.set()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
