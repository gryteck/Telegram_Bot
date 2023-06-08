import logging
import random
import asyncio
import asyncpg
import sys

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import link
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from src.config import bot, dp, admins, db_url, db_url_local, db_url_docker, supp_id, daily_views, liked_buffer
from src.wait import Wait
from decor.promo import photo_id
import decor.kawaii as t
import decor.basic as b
import decor.keyboard as k
from db.schema import BotDB
