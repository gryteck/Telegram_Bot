import json
from database import redis


class User:
    def __init__(self, data):
        self.__dict__.update(json.loads(data))


class RedisDB:
    @classmethod
    async def get_data(cls, id: int):
        async with redis.client() as conn:
            data = await conn.get(f'fsm:{id}:{id}:data')
            return User(json.loads(data))

    @classmethod
    async def get_state(cls, id: int):
        async with redis.client() as conn:
            return await conn.get(f'fsm:{id}:{id}:state')

    @classmethod
    async def update_data(cls, id: int, **kwargs):
        async with redis.client() as conn:
            try:
                data = await conn.get(f'fsm:{id}:{id}:data')
                data = json.loads(data)
            except TypeError:
                data = dict()
            for key, value in kwargs.items():
                data[key] = value
            await conn.set(f'fsm:{id}:{id}:data', json.dumps(data, ensure_ascii=False))

    @classmethod
    async def update_state(cls, id: int, state: str):
        async with redis.client() as conn:
            await conn.set(f'fsm:{id}:{id}:state', state)
