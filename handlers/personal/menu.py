from src.imp import *

BotDB = BotDB()


@dp.message_handler(state=Wait.menu_answer)
async def menu_answer(message: types.Message, state: FSMContext):
    id = message.from_user.id
    f = await BotDB.get_form(id)
    if message.text == "1":
        await message.answer(t.instruction, reply_markup=k.cont())
        await Wait.menu_answer.set()
    elif message.text == "Продолжить":
        if len(f["liked"].split()) > 1:
            await message.answer(text="сперва проверь, кому понравилась твоя анкета!", reply_markup=k.cont())
            await Wait.like_list.set()
            return
        if f['view_count'] >= daily_views:
            await message.answer("На сегодня достаточно, приходи завтра")
            await message.answer(t.menu_main_text, reply_markup=k.key_123())
            await Wait.menu_answer.set()
            return
        try:
            a = await BotDB.get_random_user(id, f["age"], f["interest"])
        except ValueError:
            await message.answer(t.no_found)
            await bot.send_photo(photo=f["photo"], caption=f["text"], chat_id=id)
            await message.answer(t.my_form_text, reply_markup=k.key_1234())
            await Wait.my_form_answer.set()
            return
        await state.update_data(liked_id=a["id"])
        await bot.send_photo(photo=f["photo"], caption=f["text"], chat_id=id, reply_markup=k.react())
        await Wait.form_reaction.set()
    elif message.text == "2":
        await bot.send_photo(photo=f["photo"], caption=f["text"], chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
    elif message.text == "3":
        await message.answer(t.delete_q, reply_markup=k.key_yesno())
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
