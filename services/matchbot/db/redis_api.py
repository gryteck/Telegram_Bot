import redis, logging


class RedisDB:
    def __init__(self):
        try:
            self.conn = redis.StrictRedis(host='localhost', port=6379, password='', db=1, charset="utf-8", decode_responses=True)
            logging.warning("Successful connection to database")
        except (redis.exceptions.ConnectionError, ConnectionRefusedError):
            logging.warning("Error during connection to database")


    def get(self, st: any):
        return self.conn.get(st)

rd = RedisDB()

print(rd.get("fsm:680359970:680359970:data"))