from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from wait import Wait
from db import BotDB
from bot import dp, bot

menu_main_text = '1. Смотреть анкеты\n2. Моя анкета\n3. Удалить анкету'
my_form_text = '1. Заполнить анкету заново\n2. Изменить текст анкеты\n3. Изменить фото\n4. Вернуться назад'


class FormDB:
    @dp.message_handler(state=Wait.choosing_gender)
    async def choose_gender(message: types.Message, state: FSMContext):
        if message.text not in ["Парень", "Девушка"]:
            await message.answer("Выберите вариант из кнопок ниже")
            return
        await state.update_data(gender=message.text.lower())

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Парни", "Девушки"]
        keyboard.add(*buttons)
        await message.answer("Кто вас интересует?", reply_markup=keyboard)
        await Wait.choosing_interest.set()


    @dp.message_handler(state=Wait.choosing_interest)
    async def choose_interest(message: types.Message, state: FSMContext):
        if message.text == "Парни" or message.text == "Девушки":
            await state.update_data(interest=message.text.lower())
            await message.answer("Введите своё имя", reply_markup=types.ReplyKeyboardRemove())
            await Wait.name.set()
        else:
            await message.answer("Выберите вариант из кнопок ниже")
            return


    @dp.message_handler(state=Wait.name)
    async def name(message: types.Message, state: FSMContext):
        if len(message.text) > 30:
            await message.answer("Слишком длинное имя")
            return
        await state.update_data(name=message.text)
        await message.answer("Сколько вам лет?")
        await Wait.age.set()


    @dp.message_handler(state=Wait.age)
    async def age(message: types.Message, state: FSMContext):
        try:
            if 10 > int(message.text) or int(message.text) > 100:
                await message.answer("Некорректный возраст")
                return
        except(TypeError, ValueError):
            await message.answer("Некорректный возраст")
            return
        await state.update_data(age=message.text)
        await message.answer("Напишите свой город")
        await Wait.city.set()


    @dp.message_handler(state=Wait.city)
    async def city(message: types.Message, state: FSMContext):
        if len(message.text) > 30:
            await message.answer("Слишком длинный город")
            return

        await state.update_data(city=message.text)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Оставить пустым")

        await message.answer("Введите описание анкеты до 200 символов (вы можете оставить его пустым и заполнить позже)",
                             reply_markup=keyboard)
        await Wait.text.set()


    @dp.message_handler(state=Wait.text)
    async def text(message: types.Message, state: FSMContext):
        if message.text == "Оставить пустым":
            await state.update_data(text='')
        else:
            if len(message.text) > 200:
                await message.answer("Описание может быть длиной не более 200 символов")
                return
            await state.update_data(text=message.text)

        await message.answer("Загрузите своё фото", reply_markup=types.ReplyKeyboardRemove())
        await Wait.photo.set()


    @dp.message_handler(state=Wait.photo, content_types=["photo"])
    async def download_photo(message: types.Message, state: FSMContext):
        await message.photo[-1].download(destination_file=f"photos/{message.from_user.id}.jpg")
        await state.update_data(liked="0", username=message.from_user.username, count=1)
        data = await state.get_data()
        d = list(data.values())
        print(d)

        BotDB.add_form(message.from_user.id, d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7])

        caption = bot.show_form(d[2], d[3], d[4], d[5])
        await message.answer("Вот ваша анкета:")
        await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"),caption=caption,
                             chat_id=message.from_user.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup=keyboard)
        await Wait.menu_answer.set()