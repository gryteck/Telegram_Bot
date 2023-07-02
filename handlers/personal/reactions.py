from src.imp import *

BotDB = BotDB()


@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text not in ("Продолжить", "Вернуться назад", "❤️", "👎", "🚫"):
        await message.reply("Нет такого варианта ответа")
        return
    if message.text == "Вернуться назад":
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()
        return
    elif message.text == "🚫":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        await Wait.claim.set()
        return
    f = BotDB.get_form(id)
    if f['view_count'] >= daily_views:
        await message.answer("На сегодня достаточно, приходи завтра")
        await message.answer(t.menu_main_text, reply_markup=kb.key_123())
        await Wait.menu_answer.set()
        return
    data = await state.get_data()
    liked_id = data["liked_id"]
    l = BotDB.get_form(liked_id)
    # реклама и прочее
    if f["view_count"] % 30 == 0 and message.text != "❤️":
        await message.answer(text=t.notice, reply_markup=kb.cont())
        await Wait.form_reaction.set()
        return
    elif f["view_count"] % 10 == 0 and message.text != "❤️":
        await bot.send_photo(photo=photo_id[random.randint(0, len(photo_id) - 1)], chat_id=id,
                             caption=t.ad[random.randint(0, len(t.ad) - 1)], parse_mode="HTML",
                             reply_markup=kb.cont())
        await Wait.form_reaction.set()
        return
    # обработка реакции
    if message.text == ("❤️" or "👎") and l['id'] in f['liked'].split():
        f['liked'] = BotDB.patch_liked(id, b.crop_list(f["liked"]))
        if not f["visible"] and len(f["liked"].split()) < liked_buffer: BotDB.patch_visible(id, True)
        if message.text == "❤️":
            await bot.send_message(text=t.like_match, chat_id=liked_id, reply_markup=kb.cont())
            await bot.send_photo(photo=f["photo"], chat_id=liked_id, caption=f["text"], reply_markup=kb.match(id))
            await bot.send_message(text=t.like_match, chat_id=id, reply_markup=kb.match(liked_id))
    elif message.text == "❤️" and l["visible"] and not f["banned"]:
        if len(l["liked"].split()) >= liked_buffer: BotDB.patch_visible(liked_id, False)
        if str(id) not in l["liked"].split():
            await bot.send_message(text=t.liked, chat_id=liked_id)
            await BotDB.patch_liked(liked_id, l["liked"]+f" {str(id)}")
    # вывод рандомной анкеты
    await random_form(message, state, id, f)

async def random_form(message: types.Message, state: FSMContext, id: int, f: dict):
    if len(f["liked"].split()) > 1:
        while not BotDB.user_exists(f["liked"].split()[-1]) and len(f["liked"].split()) != 1:
            f["liked"] = b.crop_list(f["liked"])
        BotDB.patch_liked(id, f["liked"])
        if len(f["liked"].split()) != 1:
            l = BotDB.get_form(f["liked"].split()[-1])
            await state.update_data(liked_id=l["id"])
            await bot.send_photo(photo=l["photo"], chat_id=id, caption=t.like_list+b.cap(l), reply_markup=kb.react())
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
