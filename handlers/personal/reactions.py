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
    data = await state.get_data()
    BotDB.update_date(id, daily_views)
    count = BotDB.get_count(id)
    if count >= daily_views:
        await message.answer("На сегодня достаточно, приходи завтра")
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
        return
    liked_id = data["liked_id"]
    await state.update_data(count=count+1)
    if count % 30 == 0 and message.text != "❤️":
        await message.answer(text=t.notice, reply_markup=k.cont())
        await Wait.form_reaction.set()
        return
    elif count % 10 == 0 and message.text != "❤️":
        await bot.send_photo(photo=photo_id[random.randint(0, len(photo_id)-1)], chat_id=id,
                             caption=t.ad[random.randint(0, len(t.ad) - 1)], parse_mode="HTML",
                             reply_markup=k.cont())
        await Wait.form_reaction.set()
        return
    if message.text == "❤️" and BotDB.form_exists(liked_id) and not BotDB.user_banned(id):
        liked_str = BotDB.get_user_liked(liked_id)
        if len(liked_str.split()) >= liked_buffer: BotDB.update_visible(liked_id, False)
        if str(id) not in liked_str.split():
            await bot.send_message(text=t.liked, chat_id=liked_id)
            BotDB.update_liked(liked_id, liked_str+" "+str(id))
            BotDB.update_date(id, daily_views)
    if len(BotDB.get_user_liked(id).split()) > 1:
        while len(BotDB.get_user_liked(id).split()) != 1:
            liked_str = str(BotDB.get_user_liked(message.from_user.id))
            liked_id = liked_str.split()[-1]
            if BotDB.form_exists(liked_id): break
            BotDB.update_liked(id, b.crop_list(liked_str))
        liked_str = str(BotDB.get_user_liked(id))
        if len(BotDB.get_user_liked(id).split()) != 1:
            liked_id = liked_str.split()[-1]
            await state.update_data(liked_id=liked_id)
            await message.answer(t.like_list, reply_markup=k.react())
            await bot.send_photo(photo=b.ph(liked_id), chat_id=id, caption=b.cap(liked_id))
            await Wait.like_list.set()
            return
    try:
        f = b.get_random_form(id)
    except ValueError:
        await message.answer(t.no_found)
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
        return
    await state.update_data(liked_id=f[1])
    await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.react())
    await Wait.form_reaction.set()


@dp.message_handler(state=Wait.like_list)
async def like_list(message: types.Message, state: FSMContext):
    if message.text not in ("Продолжить", "Вернуться назад", "❤️", "👎", "🚫"):
        await message.reply("Нет такого варианта ответа")
        return
    data = await state.get_data()
    liked_id = data["liked_id"]
    id = message.from_user.id
    if message.text in ("❤️", "👎", "🚫"): BotDB.update_liked(id, b.crop_list(BotDB.get_user_liked(id)))
    liked_str = BotDB.get_user_liked(id)
    if len(liked_str.split()) < liked_buffer: BotDB.update_visible(id, True)
    if message.text == "❤️" and BotDB.form_exists(liked_id):
        await bot.send_message(text=t.like_match, chat_id=liked_id, reply_markup=k.cont())
        await bot.send_photo(photo=b.ph(id), chat_id=liked_id, caption=b.cap(id), reply_markup=k.match(id))
        await bot.send_message(text=t.like_match, chat_id=id, reply_markup=k.match(liked_id))
        await message.answer(text="Продолжить смотреть тех кто тебя лайкнул?", reply_markup=k.cont())
        await Wait.like_list.set()
    elif message.text == "Продолжить" or message.text == "👎" or not BotDB.form_exists(liked_id):
        while len(BotDB.get_user_liked(id).split()) != 1 and not BotDB.form_exists(liked_str.split()[-1]):
            liked_id = BotDB.get_user_liked(id).split()[-1]
            if BotDB.form_exists(liked_id): break
            BotDB.update_liked(id, b.crop_list(BotDB.get_user_liked(id)))
        if len(BotDB.get_user_liked(id).split()) != 1:
            liked_id = liked_str.split()[-1]
            await state.update_data(liked_id=liked_id)
            await message.answer(t.like_list, reply_markup=k.react())
            await bot.send_photo(photo=b.ph(liked_id), chat_id=id, caption=b.cap(liked_id))
            await Wait.like_list.set()
        else:
            try:
                f = b.get_random_form(id)
            except ValueError:
                await message.answer(t.no_found)
                await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
                await message.answer(t.my_form_text, reply_markup=k.key_1234())
                await Wait.my_form_answer.set()
                return
            await state.update_data(liked_id=f[1])
            await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.react())
            await Wait.form_reaction.set()
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=k.key_1234())
        await Wait.claim_liked.set()
    elif message.text == "Вернуться назад":
        await bot.send_photo(photo=b.ph(id), caption=b.cap(id), chat_id=id)
        await message.answer(t.menu_main_text, reply_markup=k.key_123())
        await Wait.menu_answer.set()
