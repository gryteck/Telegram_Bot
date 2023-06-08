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
    banned_id = data["liked_id"]
    b = await BotDB.get_form(banned_id)
    f = await BotDB.get_form(id)
    if int(key) in range(1, 4):
        if str(id) not in b["noticed"].split():
            await BotDB.patch_claims(banned_id, b["noticed"]+f" {str(id)}", b["claims"]+f" {key}")
    if key == "3":
        await message.reply(t.claim_text, reply_markup=k.back())
        await Wait.claim_text.set()
        return
    try:
        a = await BotDB.get_random_user(id, f["age"], f["interest"])
    except ValueError:
        await message.answer(t.no_found)
        await bot.send_photo(photo=f["photo"], caption=f["text"], chat_id=id)
        await message.answer(t.my_form_text, reply_markup=k.key_1234())
        await Wait.my_form_answer.set()
        return
    await message.answer(t.ban_thq)
    await state.update_data(liked_id=a["id"])
    await bot.send_photo(photo=f["photo"], caption=f["text"], chat_id=id, reply_markup=k.react())
    await Wait.form_reaction.set()


@dp.message_handler(state=Wait.claim_text)
async def claim_text(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "Вернуться назад":
        await message.answer(t.ban, reply_markup=k.key_1234())
        await Wait.claim.set()
        return
    data = await state.get_data()
    banned_id = data["liked_id"]
    await bot.send_photo(photo=b.ph(banned_id), chat_id=supp_id,
                         caption="#claim "+str(banned_id)+"\n"+b.cap(banned_id)+f"\n\nFrom {id}:\n"+message.text)
    await message.answer(t.ban_thq)
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


@dp.message_handler(state=Wait.claim_liked)
async def claim_liked(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text not in ("1", "2", "3", "4"):
        await message.reply("Нет такого варианта ответа")
        await Wait.claim_liked.set()
        return
    liked_str = str(BotDB.get_user_liked(id))
    key = message.text
    data = await state.get_data()
    banned_id = data["liked_id"]
    if key == "3":
        await message.reply(t.claim_text, reply_markup=k.back())
        await Wait.claim_text_liked.set()
        return
    elif int(key) in range(1, 3):
        if not BotDB.ban_exists(banned_id): BotDB.add_ban(banned_id)
        if str(id) not in BotDB.get_noticed(banned_id).split():
            BotDB.update_noticed(banned_id, BotDB.get_noticed(banned_id) + " " + str(id))
            BotDB.update_claims(banned_id, BotDB.get_user_claims(banned_id) + " " + key)
        await message.answer(t.ban_thq)
    if len(liked_str.split()) > 1:
        liked_id = liked_str.split()[-1]
        await state.update_data(liked_id=liked_id)
        await message.answer(t.like_list, reply_markup=k.react())
        await bot.send_photo(photo=b.ph(liked_id), chat_id=id, caption=b.cap(liked_id))
        BotDB.update_liked(id, b.crop_list(liked_str))
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
        await message.answer(t.ban_thq)
        await state.update_data(liked_id=f[1])
        await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.react())
        await Wait.form_reaction.set()


@dp.message_handler(state=Wait.claim_text_liked)
async def claim_text_liked(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "Вернуться назад":
        await message.answer(t.ban, reply_markup=k.key_1234())
        await Wait.claim_liked.set()
        return
    data = await state.get_data()
    banned_id = data["liked_id"]
    if not BotDB.ban_exists(banned_id): BotDB.add_ban(banned_id)
    if str(id) not in BotDB.get_noticed(banned_id).split():
        BotDB.update_noticed(banned_id, BotDB.get_noticed(banned_id)+" "+str(id))
        BotDB.update_claims(banned_id, BotDB.get_user_claims(banned_id)+" 3")
    await message.answer(t.ban_thq)
    await bot.send_photo(photo=b.ph(banned_id), chat_id=supp_id,
                         caption="#claim " + banned_id+"\n"+b.cap(banned_id)+"\nComment: "+message.text)
    liked_str = BotDB.get_user_liked(id)
    if len(liked_str.split()) < liked_buffer: BotDB.update_visible(id, True)
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
        await message.answer(t.ban_thq)
        await state.update_data(liked_id=f[1])
        await bot.send_photo(photo=b.ph(f[1]), caption=f[0], chat_id=id, reply_markup=k.react())
        await Wait.form_reaction.set()
