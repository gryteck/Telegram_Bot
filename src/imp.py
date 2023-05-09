import logging
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import link
from aiogram.contrib.fsm_storage.redis import RedisStorage2

import decor.kawaii as t
import decor.basic as b
from src.wait import Wait
import decor.keyboard as k
from db.db import BotDB
from src.config import bot, dp, admins, db_url, db_url_local, supp_id, daily_views, liked_buffer
