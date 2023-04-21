from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token="5911241134:AAHuxXDW48E6rg8S5E_byTSWhIxQmMSDIk8")
dp = Dispatcher(bot, storage=MemoryStorage())