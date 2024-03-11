from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

media_groups = []


class Settings(BaseSettings):
    MODE: Literal['DEV', 'TEST', 'PROD']

    SLEEP_TIME: int
    DAILY_VIEWS: int
    LIKED_BUFFER: int
    LAST_ACTIVE_TIME: str
    BAN_LIMIT: int

    SUPPORT_ID: int

    PROMO_URL: str

    TOKEN: str

    SUPPORT_ID: int

    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASS: str
    PG_NAME: str

    RD_HOST: str
    RD_PASS: str

    @property
    def PG_URL(self):
        return f"postgresql+asyncpg://" \
               f"{self.PG_USER}:" \
               f"{self.PG_PASS}@" \
               f"{self.PG_HOST}:" \
               f"{self.PG_PORT}/" \
               f"{self.PG_NAME}"

    @property
    def RD_URL(self):
        return f"redis://{self.RD_PASS}@{self.RD_HOST}:6379/1"

    TEST_TOKEN: str

    TEST_PG_HOST: str
    TEST_PG_PORT: int
    TEST_PG_USER: str
    TEST_PG_PASS: str
    TEST_PG_NAME: str

    TEST_RD_HOST: str
    TEST_RD_PASS: str

    @property
    def TEST_PG_URL(self):
        return f"postgresql+asyncpg://" \
               f"{self.TEST_PG_USER}:" \
               f"{self.TEST_PG_PASS}@" \
               f"{self.TEST_PG_HOST}:" \
               f"{self.TEST_PG_PORT}/" \
               f"{self.TEST_PG_NAME}"

    @property
    def TEST_RD_URL(self):
        return f"redis://{self.TEST_RD_PASS}@{self.TEST_RD_HOST}:6379/1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


settings = Settings()


if settings.MODE == 'TEST':
    bot = Bot(token=settings.TEST_TOKEN)
    dp = Dispatcher(bot, storage=RedisStorage2(host=settings.TEST_RD_HOST, db=1, password=settings.TEST_RD_PASS))
else:
    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher(bot, storage=RedisStorage2(host=settings.RD_HOST, db=1, password=settings.RD_PASS))
