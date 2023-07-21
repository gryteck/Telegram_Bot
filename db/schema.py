import psycopg2
import logging
from src.config import db_url, inactive_day, inactive_time, last_active_time


def db_exception(func):
    def inner(self, *args, **kwargs):
        try:
            res = func(self, *args, **kwargs)
        except psycopg2.Error as e:
            logging.warning(e)
            self.close()
            self.__init__()
            res = None
        return res

    return inner

class BotDB:
    def __init__(self):
        self.conn = psycopg2.connect(db_url)
        self.cursor = self.conn.cursor()
        logging.warning("Successful connection to database")

    def connect(self):
        pass

    def close(self):
        logging.warning("Connection closed")
        self.conn.close()

    @db_exception
    def user_exists(self, id: int) -> bool:
        self.cursor.execute("SELECT user_id FROM users WHERE id = %s", (id,))
        return bool(len(self.cursor.fetchall()))

    @db_exception
    def get_form(self, id: int) -> dict:
        self.cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        row = self.cursor.fetchone()
        column_names = [desc[0] for desc in self.cursor.description]
        user_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        return user_dict

    @db_exception
    def get_form_by_username(self, username: str) -> dict:
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = self.cursor.fetchone()
        column_names = [desc[0] for desc in self.cursor.description]
        user_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        return user_dict

    @db_exception
    def get_random_user(self, id: int, age: int, interest: str) -> dict:
        if interest == 'Девушки':
            self.cursor.execute("SELECT * FROM users WHERE id != %s AND age BETWEEN %s AND %s "
                                "AND gender = 'Девушка' AND banned = false AND visible = true "
                                "ORDER BY RANDOM() LIMIT 1",
                                (id, age - 5, age + 2))
            row = self.cursor.fetchone()
            column_names = [desc[0] for desc in self.cursor.description]
        else:
            self.cursor.execute("SELECT * FROM users WHERE id != %s AND age BETWEEN %s AND %s "
                                "AND gender = 'Парень' AND banned = false AND visible = true "
                                "ORDER BY RANDOM() LIMIT 1",
                                (id, age - 2, age + 5))
            row = self.cursor.fetchone()
            column_names = [desc[0] for desc in self.cursor.description]
        if row is None:
            raise ValueError
        else:
            user_data = {}
            for i in range(len(column_names)):
                user_data[column_names[i]] = row[i]
            # print("okay", user_data)
            return user_data

    @db_exception
    def get_random_claim(self):
        self.cursor.execute("SELECT * FROM users WHERE claims is not null ORDER BY RANDOM() LIMIT 1")
        row = self.cursor.fetchone()
        column_names = [desc[0] for desc in self.cursor.description]
        user_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        return user_dict

    @db_exception
    def get_noticed(self, id: int) -> list:
        result = self.cursor.fetch("SELECT noticed FROM users WHERE id = %s", (id,))
        return result[0]

    @db_exception
    def post_user(self, username: str, id: int, gender: str, interest: str, name: str, age: int, photo: str, text: str):
        self.cursor.execute("INSERT INTO users (username, id, name, age, photo, text, gender, interest, liked, "
                            "claims, noticed) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (username, id, name, age, photo, text, gender, interest, [], [], []))
        return self.conn.commit()

    @db_exception
    def patch_user(self, id: int, gender: str, interest: str, name: str, age: int, photo: str, text: str) -> None:
        self.cursor.execute("UPDATE users SET name = %s, gender = %s, interest = %s, age = %s, photo = %s, text = %s"
                            " WHERE id = %s", (name, gender, interest, age, photo, text, id,))
        return self.conn.commit()

    @db_exception
    def patch_visible(self, id: int, visible: bool) -> None:

        self.cursor.execute("UPDATE users SET visible = %s WHERE id = %s", (visible, id,))
        return self.conn.commit()

    @db_exception
    def patch_text(self, id: int, text: str) -> None:
        self.cursor.execute("UPDATE users SET text = %s WHERE id = %s", (text, id,))
        return self.conn.commit()

    @db_exception
    def patch_liked(self, id: int, liked: list) -> list:
        self.cursor.execute("UPDATE users SET liked = %s WHERE id = %s", (liked, id,))
        self.conn.commit()
        return liked

    @db_exception
    def patch_photo(self, id: int, photo: str) -> None:
        self.cursor.execute("UPDATE users SET photo = %s WHERE id = %s", (photo, id,))
        return self.conn.commit()

    @db_exception
    def patch_claims(self, id: int, noticed: str, claims: list) -> None:
        self.cursor.execute("UPDATE users SET noticed = %s, claims = %s WHERE id = %s", (noticed, claims, id,))
        return self.conn.commit()

    @db_exception
    def patch_ban(self, id: int, ban: bool) -> None:
        self.cursor.execute("UPDATE users SET banned = %s WHERE id = %s", (ban, id,))
        return self.conn.commit()

    @db_exception
    def patch_count(self, id) -> None:
        self.cursor.execute("UPDATE users SET view_count = view_count+1 WHERE id = %s", (id,))
        self.cursor.execute("UPDATE users SET view_count = 1 WHERE id = %s AND ((NOW() - "
                            "(SELECT active_date FROM users WHERE id = %s) > interval %s))",
                            (id, id, last_active_time,))
        self.cursor.execute("UPDATE users SET active_date = NOW() WHERE id = %s AND ((NOW() - "
                            "(SELECT active_date FROM users WHERE id = %s) > interval %s))",
                            (id, id, last_active_time,))
        return self.conn.commit()

    @db_exception
    def patch_inactive_users(self) -> list:
        self.cursor.execute(
            "SELECT id FROM users WHERE visible = true AND ((NOW() - active_date) > INTERVAL %s)", (inactive_time,))
        row = [result[0] for result in self.cursor.fetchall()]
        self.cursor.execute("UPDATE users SET visible = false "
                            "WHERE visible = true AND ((NOW() - active_date) > INTERVAL %s)", (inactive_time,))
        if row is None:
            return []
        else:
            return row

    @db_exception
    def patch_daily_inactive_users(self) -> list:
        self.cursor.execute(
            "SELECT id FROM users WHERE visible = true AND ((NOW() - active_date) > INTERVAL %s) AND view_count > 2",
            (inactive_day,))
        row = [result[0] for result in self.cursor.fetchall()]
        self.cursor.execute("UPDATE users SET view_count = 1 "
                            "WHERE visible = true AND ((NOW() - active_date) > INTERVAL %s) AND view_count > 2",
                            (inactive_day,))
        if row is None:
            return []
        else:
            return row

    @db_exception
    def create_table_users(self):
        create_table = (
            """CREATE TABLE users (
                    user_id SMALLSERIAL PRIMARY KEY,
                    id BIGINT NOT NULL UNIQUE,
                    username TEXT,
                    name TEXT NOT NULL,
                    age SMALLINT NOT NULL,
                    photo TEXT NOT NULL,
                    text TEXT,
                    gender TEXT NOT NULL,
                    interest TEXT NOT NULL,
                    liked BIGINT ARRAY NOT NULL,
                    join_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    active_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    view_count SMALLINT DEFAULT 1 NOT NULL,
                    claims_count SMALLINT DEFAULT 0 NOT NULL,
                    claims TEXT ARRAY NOT NULL,
                    banned BOOLEAN DEFAULT false NOT NULL,
                    noticed INT ARRAY NOT NULL,
                    visible BOOLEAN DEFAULT true NOT NULL
                    );
                    CREATE INDEX user_id_idx ON users (id);"""
        )
        self.cursor.execute(create_table)
        return self.conn.commit()

    @db_exception
    def table_users_exists(self):
        query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'users'
                    );
                """
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    @db_exception
    def drop_table_users(self):
        self.cursor.execute("DROP TABLE users")
        return self.conn.commit()


db = BotDB()
