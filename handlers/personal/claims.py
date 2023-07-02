from src.imp import *

BotDB = BotDB()


@dp.message_handler(state=Wait.claim)
async def claim(message: types.Message, state: FSMContext):
    if message.text not in ("1", "2", "3", "4"):
        await message.reply("Нет такого варианта ответа")
        await Wait.claim.set()
        return
    id, key = message.from_user.id, message.text
    data = await state.get_data()
    liked_id = data["liked_id"]
    l = BotDB.get_form(liked_id)
    f = BotDB.get_form(id)
    if int(key) in range(1, 4):
        if str(id) not in l["noticed"].split():
            BotDB.patch_claims(liked_id, l["noticed"]+f" {str(id)}", l["claims"]+f" {key}")
    if key == "3":
        await message.reply(t.claim_text, reply_markup=kb.back())
        await Wait.claim_text.set()
        return
    # вывод анкеты
    if len(f["liked"].split()) > 1:
        while not BotDB.user_exists(f["liked"].split()[-1]) and len(f["liked"].split()) != 1:
            f["liked"] = b.crop_list(f["liked"])
        if key != "4": f["liked"] = b.crop_list(f["liked"])
        BotDB.patch_liked(id, f["liked"])
        if len(f["liked"].split()) != 1:
            l = BotDB.get_form(f["liked"].split()[-1])
            await state.update_data(liked_id=l["id"])
            await bot.send_photo(photo=l["photo"], chat_id=id, caption=t.like_list+l["text"], reply_markup=kb.react())
            await Wait.like_list.set()
            return
    try:
        r = BotDB.get_random_user(id, f["age"], f["interest"])
    except ValueError:
        await message.answer(t.no_found)
        await bot.send_photo(photo=f["photo"], caption=f["text"], chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await Wait.my_form_answer.set()
        return
    await message.answer(t.ban_thq)
    await state.update_data(liked_id=r["id"])
    await bot.send_photo(photo=r["photo"], caption=r["text"], chat_id=id, reply_markup=kb.react())
    await Wait.form_reaction.set()


@dp.message_handler(state=Wait.claim_text)
async def claim_text(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "Вернуться назад":
        await message.answer(t.ban, reply_markup=kb.key_1234())
        await Wait.claim.set()
        return
    data = await state.get_data()
    liked_id = data["liked_id"]
    l = BotDB.get_form(liked_id)
    f = BotDB.get_form(id)
    await bot.send_photo(photo=l['photo'], chat_id=supp_id,
                         caption="#claim "+str(liked_id)+"\n"+b.cap(l)+f"\n\nFrom {id}:\n"+message.text)
    await message.answer(t.ban_thq)
    # вывод анкеты
    if len(f["liked"].split()) > 1:
        while not BotDB.user_exists(f["liked"].split()[-1]) and len(f["liked"].split()) != 1:
            f["liked"] = b.crop_list(f["liked"])
        BotDB.patch_liked(id, b.crop_list(f["liked"]))
        if len(f["liked"].split()) != 1:
            l = BotDB.get_form(f["liked"].split()[-1])
            await state.update_data(liked_id=l["id"])
            await bot.send_photo(photo=l["photo"], chat_id=id, caption=t.like_list + l["text"], reply_markup=kb.react())
            await Wait.like_list.set()
            return
    try:
        r = BotDB.get_random_user(id, f["age"], f["interest"])
    except ValueError:
        await message.answer(t.no_found)
        await bot.send_photo(photo=f['photo'], caption=b.cap(id), chat_id=id)
        await message.answer(t.my_form_text, reply_markup=kb.key_1234())
        await Wait.my_form_answer.set()
        return
    await state.update_data(liked_id=f[1])
    await bot.send_photo(photo=r['photo'], caption=b.cap(r), chat_id=id, reply_markup=kb.react())
    await Wait.form_reaction.set()
