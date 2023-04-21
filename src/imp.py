import logging
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext


import decor.text as t
import decor.basic as b
from src.wait import Wait
import decor.keyboard as k
from db.db import BotDB
from src.config import bot, dp
