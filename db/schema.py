import psycopg2
from src.config import db_url, db_url_local, db_url_docker, time, daily_views


class BotDB:
    def __init__(self):
        self.conn = psycopg2.connect(db_url_local)
        self.cursor = self.conn.cursor()
        print("some connection")

    def connect(self):
        pass

    def close(self):
        print("some disconnection")
        self.conn.close()

    def user_exists(self, id: int):
        self.cursor.execute("SELECT user_id FROM users WHERE id = %s", (id,))
        return bool(len(self.cursor.fetchall()))

    def get_form(self, id: int):
        self.cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        row = self.cursor.fetchone()
        column_names = [desc[0] for desc in self.cursor.description]
        user_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        return user_dict

    def get_form_by_username(self, username: str):
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = self.cursor.fetchone()
        column_names = [desc[0] for desc in self.cursor.description]
        user_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        return user_dict

    def get_random_user(self, id: int, age: int, interest: str):
        if interest == 'девушки':
            self.cursor.execute("SELECT * FROM users WHERE id != %s AND age BETWEEN %s AND %s "
                                "AND gender = 'девушка' AND banned = false AND visible = true "
                                "ORDER BY RANDOM() LIMIT 1",
                                (id, age - 5, age + 2))
            row = self.cursor.fetchone()
            column_names = [desc[0] for desc in self.cursor.description]
        else:
            self.cursor.execute("SELECT * FROM users WHERE id != %s AND age BETWEEN %s AND %s "
                                "AND gender = 'парень' AND banned = false AND visible = true "
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
            print("okay", user_data)
            return user_data

    def get_random_claim(self):
        self.cursor.execute("SELECT * FROM users WHERE claims != '0' ORDER BY RANDOM() LIMIT 1")
        row = self.cursor.fetchone()
        column_names = [desc[0] for desc in self.cursor.description]
        user_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        return user_dict

    def get_noticed(self, id: int):
        result = self.cursor.fetch("SELECT noticed_users FROM users WHERE id = %s", (id,))
        return result[0]

    def post_user(self, username: str, id: int, gender: str, interest: str, name: str, age: int, photo: str, text: str):
        self.cursor.execute("INSERT INTO users (username, id, name, age, photo, text, gender, interest, liked) "
                            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (username, id, name, age, photo, text, gender, interest, "0"))
        return self.conn.commit()

    def patch_user(self, id: int, gender: str, interest: str, name: str, age: int, photo: str, text: str):
        self.cursor.execute("UPDATE users SET name = %s, gender = %s, interest = %s, age = %s, photo = %s, text = %s"
                            " WHERE id = %s", (name, gender, interest, age, photo, text, id,))
        return self.conn.commit()

    def patch_visible(self, id: int, visible: bool):
        self.cursor.execute("UPDATE users SET visible = %s WHERE id = %s", (visible, id,))
        return self.conn.commit()

    def patch_text(self, id: int, text: str):
        self.cursor.execute("UPDATE users SET text = %s WHERE id = %s", (text, id,))
        return self.conn.commit()

    def patch_liked(self, id: int, liked: str):
        self.cursor.execute("UPDATE users SET liked = %s WHERE id = %s", (liked, id,))
        return liked

    def patch_photo(self, id: int, photo: str):
        self.cursor.execute("UPDATE users SET photo = %s WHERE id = %s", (photo, id,))
        return self.conn.commit()

    def patch_claims(self, id: int, noticed: str, claims: str):
        self.cursor.execute("UPDATE users SET noticed_users = %s, claims = %s WHERE id = %s", (noticed, claims, id,))
        return self.conn.commit()

    def patch_ban(self, id: int, ban: bool):
        self.cursor.execute("UPDATE users SET ban = %s WHERE id = %s", (ban, id,))
        return self.conn.commit()

    def patch_count(self, id):
        self.cursor.execute("UPDATE users SET view_count = view_count+1 WHERE id = %s", (id,))
        self.cursor.execute("UPDATE users SET view_count = 1 WHERE id = %s AND ((NOW() - "
                            "(SELECT active_date FROM users WHERE id = %s) > interval %s))", (id, id, time,))
        self.cursor.execute("UPDATE users SET active_date = NOW() WHERE id = %s AND ((NOW() - "
                            "(SELECT active_date FROM users WHERE id = %s) > interval %s))", (id, id, time,))
        return self.conn.commit()
