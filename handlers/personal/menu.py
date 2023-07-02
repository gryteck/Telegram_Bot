from src.imp import *
BotDB = BotDB()


@dp.message_handler(state=Wait.menu_answer)
async def menu_answer(message: types.Message, state: FSMContext):
    id = message.from_user.id
    f = BotDB.get_form(id)
    if message.text == "1":
        await message.answer(t.instruction, reply_markup=kb.cont())
        await Wait.menu_answer.set()
    elif message.text == "Продолжить":
        if len(f["liked"].split()) > 1:
            while not BotDB.user_exists(f["liked"].split()[-1]) and len(f["liked"].split()) != 1:
                f["liked"] = b.crop_list(f["liked"])
            BotDB.patch_liked(id, f["liked"])
            if len(f["liked"].split()) != 1:
                l = BotDB.get_form(f["liked"].split()[-1])
                await state.update_data(liked_id=l["id"])
                await bot.send_photo(photo=l["photo"], chat_id=id, caption=t.like_list + b.cap(l),
                                     reply_markup=kb.react())
                await Wait.form_reaction.set()
                return
        try:
            r = BotDB.get_random_user(id, f["age"], f["interest"])
        except ValueError:
            await message.answer(t.no_found)
            await bot.send_photo(photo=f["photo"], caption=b.cap(f), chat_id=id)
            await message.answer(t.my_form_text, reply_markup=kb.key_1234())
            await Wait.my_form_answer.set()
            return
        await state.update_data(liked_id=r["id"])
        await bot.send_photo(photo=r["photo"], caption=b.cap(r), chat_id=id, reply_markup=kb.react())
        await Wait.form_reaction.set()
    elif message.text == "2":
        await bot.send_photo(photo=f["photo"], caption=b.cap(f), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await Wait.my_form_answer.set()
    elif message.text == "3":
        await message.answer(t.delete_q, reply_markup=kb.key_yesno())
        await Wait.delete_confirm.set()
    else:
        await message.reply("Нет такого варианта ответа")
        return


@dp.message_handler(state=Wait.instructions, content_types=["photo"])
async def instruction(message: types.Message, state: FSMContext):
    id = message.from_user.id
    photo = message.photo[-1].file_id
    await message.answer(text=photo)
    await Wait.instructions.set()
