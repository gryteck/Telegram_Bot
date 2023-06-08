from src.imp import *

BotDB = BotDB()


@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text not in ("Продолжить", "Вернуться назад", "❤️", "👎", "🚫"):
        await message.reply("Нет такого варианта ответа")
        return
    if message.text == "Вернуться назад":
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
        return
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=k.key_1234())
        await Wait.claim.set()
        return
    f = await BotDB.get_form(id)
    if f['view_count'] >= daily_views:
        await message.answer("На сегодня достаточно, приходи завтра")
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
        return
    data = await state.get_data()
    liked_id = data["liked_id"]
    l = await BotDB.get_form(liked_id)
    if f["view_count"] % 30 == 0 and message.text != "❤️":
        await message.answer(text=t.notice, reply_markup=k.cont())
        await Wait.form_reaction.set()
        return
    elif f["view_count"] % 10 == 0 and message.text != "❤️":
        await bot.send_photo(photo=photo_id[random.randint(0, len(photo_id) - 1)], chat_id=id,
                             caption=t.ad[random.randint(0, len(t.ad) - 1)], parse_mode="HTML",
                             reply_markup=k.cont())
        await Wait.form_reaction.set()
        return
    if message.text == "❤️" and l["visible"] and not f["banned"]:
        if len(l["liked"].split()) >= liked_buffer: await BotDB.patch_visible(liked_id, False)
        if str(id) not in l["liked"].split():
            await bot.send_message(text=t.liked, chat_id=liked_id)
            await BotDB.patch_liked(liked_id, l["liked"]+f" {str(id)}")
    # -------- Далее вывод анкеты
    if len(f["liked"].split()) > 1:
        while not await BotDB.user_exists(f["liked"].split()[-1]) and len(f["liked"].split()) != 1:
            f["liked"] = b.crop_list(f["liked"])
        await BotDB.patch_liked(id, f["liked"])
        if len(f["liked"].split()) != 1:
            a = await BotDB.get_form(f["liked"].split()[-1])
            await state.update_data(liked_id=a["id"])
            await bot.send_photo(photo=a["photo"], chat_id=id, caption=t.like_list+a["text"], reply_markup=k.react())
            await Wait.like_list.set()
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


@dp.message_handler(state=Wait.like_list)
async def like_list(message: types.Message, state: FSMContext):
    if message.text not in ("Продолжить", "Вернуться назад", "❤️", "👎", "🚫"):
        await message.reply("Нет такого варианта ответа")
        return
    data = await state.get_data()
    liked_id = data["liked_id"]
    id = message.from_user.id
    f = await BotDB.get_form(id)
    if message.text in ("❤️", "👎", "🚫"): f["liked"] = await BotDB.patch_liked(id, b.crop_list(f["liked"]))
    if len(f["liked"].split()) < liked_buffer and not f["visible"]: await BotDB.patch_visible(id, True)
    if message.text == "❤️":
        await bot.send_message(text=t.like_match, chat_id=liked_id, reply_markup=k.cont())
        await bot.send_photo(photo=f["photo"], chat_id=liked_id, caption=f["text"], reply_markup=k.match(id))
        await bot.send_message(text=t.like_match, chat_id=id, reply_markup=k.match(liked_id))
        await message.answer(text="Продолжить смотреть тех кто тебя лайкнул?", reply_markup=k.cont())
        await Wait.like_list.set()
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=k.key_1234())
        await Wait.claim_liked.set()
    elif message.text == "Вернуться назад":
        await bot.send_photo(photo=f["photo"], caption=f["photo"], chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
    else:
        if len(f["liked"].split()) > 1:
            while not await BotDB.user_exists(f["liked"].split()[-1]) and len(f["liked"].split()) != 1:
                f["liked"] = b.crop_list(f["liked"])
            await BotDB.patch_liked(id, f["liked"])
            if len(f["liked"].split()) != 1:
                a = await BotDB.get_form(f["liked"].split()[-1])
                await state.update_data(liked_id=a["id"])
                await bot.send_photo(photo=a["photo"], chat_id=id, caption=t.like_list + a["text"],
                                     reply_markup=k.react())
                await Wait.like_list.set()
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
        await bot.send_photo(photo=a["photo"], caption=a["text"], chat_id=id, reply_markup=k.react())
        await Wait.form_reaction.set()
