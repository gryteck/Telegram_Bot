import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, callback_query
import emoji

from wait import Wait
from db import BotDB
import random

bot = Bot(token="5911241134:AAHuxXDW48E6rg8S5E_byTSWhIxQmMSDIk8")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

BotDB = BotDB('database.db')

menu_main_text = '1. Смотреть анкеты\n2. Моя анкета\n3. Удалить анкету'
my_form_text = '1. Заполнить анкету заново\n2. Изменить текст анкеты\n3. Изменить фото\n4. Вернуться назад'


def show_form(name, age, city, text):
    return f'{name}\n{age}\n{city}\n{text}'


def get_random_form(list_of_forms):
    form = list_of_forms[random.randint(0, len(list_of_forms) - 1)]
    a = form
    return [show_form(a[2], a[3], a[4], a[5]), BotDB.get_photo_id(a[1])]


@dp.message_handler(commands="res", state="*")
async def restart(message: types.Message, state: FSMContext):
    BotDB.drop()


@dp.message_handler(commands="start", state="*")
async def form_start(message: types.Message, state: FSMContext):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id)

    if BotDB.form_exists(message.from_user.id):

        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        caption = show_form(a[2], a[3], a[4], a[5])
        await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), chat_id=message.from_user.id,
                             caption=caption)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup=keyboard)
        await Wait.menu_answer.set()

    else:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Парень", "Девушка"]
        keyboard.add(*buttons)

        await message.answer("Давайте заполним анкету!\nДля начала выберите свой пол", reply_markup=keyboard)
        await Wait.choosing_gender.set()


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

    data = await state.get_data()
    d = list(data.values())
    print(d)

    BotDB.add_form(message.from_user.id, d[0], d[1], d[2], d[3], d[4], d[5])
    await state.update_data(count=1)

    caption = show_form(d[2], d[3], d[4], d[5])
    await message.answer("Вот ваша анкета: ")
    await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), caption=caption,
                         chat_id=message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3"]
    keyboard.add(*buttons)

    await message.answer(menu_main_text, reply_markup=keyboard)
    await Wait.menu_answer.set()


@dp.message_handler(state=Wait.menu_answer)
async def menu_answer(message: types.Message, state: FSMContext):
    if message.text == "1":
        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        caption = show_form(a[2], a[3], a[4], a[5])

        list_of_forms = BotDB.find_forms(message.from_user.id, a[7], a[4], a[3])

        try:
            get_random_form(list_of_forms)
        except ValueError:
            await message.answer(
                "Мне не удалось подобрать вам никого")

            await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), caption=caption,
                                 chat_id=message.from_user.id)

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["1", "2", "3", "4"]
            keyboard.add(*buttons)

            await message.answer(my_form_text, reply_markup=keyboard)
            await Wait.my_form_answer.set()

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["❤️", "👎", "Вернуться назад"]
        keyboard.add(*buttons)

        form = get_random_form(list_of_forms)

        caption = form[0]
        photo_id = form[1]

        await state.update_data(liked_id=photo_id)

        await bot.send_photo(photo=open(f"photos/{photo_id}.jpg", "rb"), caption=caption, chat_id=message.from_user.id,
                             reply_markup=keyboard)

        await Wait.form_reaction.set()

    elif message.text == "2":

        """ Show form (form) in 4 strings """

        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        caption = show_form(a[2], a[3], a[4], a[5])

        await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), caption=caption,
                             chat_id=message.from_user.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3", "4"]
        keyboard.add(*buttons)

        await message.answer(my_form_text, reply_markup=keyboard)
        await Wait.my_form_answer.set()

    elif message.text == "3":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Да", "Нет"]
        keyboard.add(*buttons)
        await message.answer("Вы уверены, что хотите удалить свою анкету?", reply_markup=keyboard)
        await Wait.delete_confirm.set()

    else:
        await message.answer("Выберите вариант из кнопок ниже")
        return


@dp.message_handler(state=Wait.form_reaction)
async def form_reaction(message: types.Message, state: FSMContext):
    data = await state.get_data()
    list_of_forms = BotDB.find_forms(message.from_user.id, data["interest"], data["city"], data["age"])

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["❤️", "👎", "Вернуться назад"]
    keyboard.add(*buttons)

    form = get_random_form(list_of_forms)
    caption = form[0]
    photo_id = form[1]

    c = data["count"]
    if c % 7 == 0:
        await message.answer(text="хера ты баклажан")

    await state.update_data(count=c+1)

    if message.text == "❤️":
        liked_id = data["liked_id"]

        await bot.send_message(text="Вы понравились этому человеку: ", chat_id=liked_id)
        await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), chat_id=liked_id, caption=caption)
        await bot.send_message(text=f"Начинай общаться, если понравлися(лась) - @{message.from_user.username}", chat_id=liked_id)

        await bot.send_photo(photo=open(f"photos/{photo_id}.jpg", "rb"), caption=caption, chat_id=message.from_user.id)
        await Wait.form_reaction.set()

    elif message.text == "👎":
        await bot.send_photo(photo=open(f"photos/{photo_id}.jpg", "rb"), caption=caption, chat_id=message.from_user.id)
        await Wait.form_reaction.set()

    elif message.text == "Вернуться назад":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup=keyboard)
        await Wait.menu_answer.set()
    else:
        await message.answer("Выберите вариант из кнопок")
        return


@dp.message_handler(state=Wait.delete_confirm)
async def delete_confirm(message: types.Message, state: FSMContext):
    if message.text == "Да":
        BotDB.delete_form(message.from_user.id)
        BotDB.delete_user(message.from_user.id)
        await message.answer("Ваша анкета удалена!\nВы можете вернуться сюда в любое время по команде /start",
                             reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Нет":
        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        caption = show_form(a[2], a[3], a[4], a[5])

        await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), caption=caption,
                             chat_id=message.from_user.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3", "4"]
        keyboard.add(*buttons)

        await message.answer(my_form_text, reply_markup=keyboard)
        await Wait.my_form_answer.set()
    else:
        await message.answer("Выберите вариант из кнопок ниже")
        return


@dp.message_handler(state=Wait.my_form_answer)
async def my_form_answer(message: types.Message, state: FSMContext):
    if message.text == "1":
        BotDB.delete_form(message.from_user.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Парень", "Девушка"]
        keyboard.add(*buttons)

        await message.answer("Для начала выберите свой пол",
                             reply_markup=keyboard)
        await Wait.choosing_gender.set()
    # Enter new text
    elif message.text == "2":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Оставить пустым")
        await message.answer("Введите новый текст анкеты", reply_markup=keyboard)
        await Wait.change_text.set()

    elif message.text == "3":
        await message.answer("Отправьте новое фото", reply_markup=types.ReplyKeyboardRemove())
        await Wait.change_photo.set()

    elif message.text == "4":
        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        caption = show_form(a[2], a[3], a[4], a[5])

        await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), caption=caption,
                             chat_id=message.from_user.id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup=keyboard)
        await Wait.menu_answer.set()
    else:
        await message.answer("Выберите вариант из кнопок ниже")
        return


@dp.message_handler(state=Wait.change_text)
async def change_text(message: types.Message, state: FSMContext):
    if message.text == "Оставить пустым":
        BotDB.update_text(message.from_user.id, '')

        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        caption = show_form(a[2], a[3], a[4], a[5])

        await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), caption=caption,
                             chat_id=message.from_user.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3", "4"]
        keyboard.add(*buttons)

        await message.answer(my_form_text, reply_markup=keyboard)
        await Wait.my_form_answer.set()
    else:
        if len(message.text) > 200:
            await message.answer("Описание должно быть длиной до 200 символов")
            return
        BotDB.update_text(message.from_user.id, message.text)

        form = BotDB.get_form(message.from_user.id)
        a = form[0]
        caption = show_form(a[2], a[3], a[4], a[5])

        await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), caption=caption,
                             chat_id=message.from_user.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["1", "2", "3"]
        keyboard.add(*buttons)

        await message.answer(menu_main_text, reply_markup=keyboard)
        await Wait.menu_answer.set()


@dp.message_handler(state=Wait.change_photo, content_types=["photo"])
async def change_photo(message: types.Message, state: FSMContext):
    await message.photo[-1].download(destination_file=f"photos/{message.from_user.id}.jpg")

    form = BotDB.get_form(message.from_user.id)
    a = form[0]
    caption = show_form(a[2], a[3], a[4], a[5])

    await message.answer("Вот ваша анкета: ")
    await bot.send_photo(photo=open(f"photos/{message.from_user.id}.jpg", "rb"), caption=caption,
                         chat_id=message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2", "3"]
    keyboard.add(*buttons)

    await message.answer(menu_main_text, reply_markup=keyboard)
    await Wait.menu_answer.set()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
