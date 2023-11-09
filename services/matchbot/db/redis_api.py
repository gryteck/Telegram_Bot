import aiogram
import logging
import redis

import json


class User:
    def __init__(self, data):
        self.__dict__.update(json.loads(data))


class Wait:
    start = 'start'

    my_form_answer = 'Wait.my_form_answer'
    set_gender = 'Wait.set_gender'
    set_interest = 'Wait.set_interest'
    set_name = 'Wait.set_name'
    set_age = 'Wait.set_age'
    set_text = 'Wait.set_text'
    set_photo = 'Wait.set_photo'
    change_text = 'Wait.change_text'
    change_photo = 'Wait.change_photo'
    delete_confirm = 'Wait.delete_confirm'

    menu_answer = "Wait.menu_answer"
    instructions = 'Wait.instruction'

    form_reaction = 'Wait.form_reaction'
    cont = 'Wait.continue'

    claim = 'Wait.claim'
    claim_text = 'Wait.claim_text'

    admin = 'Wait.admin'

    get_photo = 'Wait.get_photo'


class RedisDB:
    def __init__(self):
        try:
            self.conn = redis.StrictRedis(host='localhost', port=6379, password='', db=1, charset="utf-8",
                                          decode_responses=True)
            logging.warning("Successful connection to database")
        except (redis.exceptions.ConnectionError, ConnectionRefusedError):
            logging.warning("Error during connection to database")

    def create_data(self, id: int, **kwargs):
        for key, value in kwargs.items():
            self.conn.hset(f'fsm:{id}:{id}:data', f'{key}', value)

    def get_data(self, id: int):
        return User(self.conn.get(f'fsm:{id}:{id}:data'))

    def get_state(self, id: int):
        return self.conn.get(f'fsm:{id}:{id}:state')

    def update_data(self, id: int, **kwargs):
        data = json.loads(self.conn.get(f'fsm:{id}:{id}:data'))
        for key, value in kwargs.items():
            data[f"{key}"] = value
        return self.conn.set(f'fsm:{id}:{id}:data', f"{json.dumps(data, ensure_ascii=False)}")

    def update_state(self, id: int, state: Wait):
        return self.conn.set(f'fsm:{id}:{id}:state', state)


rd = RedisDB()
