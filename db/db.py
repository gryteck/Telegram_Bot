import psycopg2
from src.config import db_url, db_url_local


class BotDB:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(db_url_local)
        except:
            print('Cant establish connection to database')
        self.cursor = self.conn.cursor()
        if not self.table_exists('users'):
            self.create_table_users()
        if not self.table_exists('forms'):
            self.create_table_forms()
        if not self.table_exists('ban'):
            self.create_table_ban()

    def table_exists(self, db_name):
        self.cursor.execute(
            f"SELECT EXISTS (SELECT 1 AS result FROM pg_tables WHERE tablename = '{db_name}');")
        return self.cursor.fetchone()[0]

    def create_table_users(self):
        query = '''CREATE TABLE users (
                    user_id SMALLSERIAL PRIMARY KEY,
                    id BIGINT NOT NULL UNIQUE,
                    join_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    active_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
                    );'''
        self.cursor.execute(query)
        return self.conn.commit()

    def create_table_forms(self):
        query = '''CREATE TABLE forms (
                    username TEXT,
                    id BIGINT NOT NULL,
                    name TEXT NOT NULL,
                    age SMALLINT NOT NULL,
                    photo TEXT NOT NULL,
                    text TEXT,
                    gender TEXT NOT NULL,
                    interest TEXT NOT NULL,
                    liked TEXT NOT NULL
                    );'''
        self.cursor.execute(query)
        return self.conn.commit()

    def create_table_ban(self):
        query = '''CREATE TABLE ban (
                    id BIGINT PRIMARY KEY NOT NULL,
                    count SMALLINT DEFAULT 0 NOT NULL,
                    claims TEXT DEFAULT 0 NOT NULL,
                    banned BOOLEAN DEFAULT false NOT NULL,
                    noticed TEXT DEFAULT 0 NOT NULL
                    );'''
        self.cursor.execute(query)
        return self.conn.commit()

    def user_exists(self, id):
        self.cursor.execute("SELECT user_id FROM users WHERE id = %s", (id,))
        return bool(len(self.cursor.fetchall()))

    def ban_exists(self, id):
        self.cursor.execute("SELECT count FROM ban WHERE id = %s", (id,))
        return bool(len(self.cursor.fetchall()))

    def user_banned(self, id):
        if self.ban_exists(id):
            self.cursor.execute("SELECT banned FROM ban WHERE id = %s", (id,))
            return self.cursor.fetchone()[0]
        else:
            return False

    def form_exists(self, id):
        self.cursor.execute("SELECT COUNT (*) FROM forms WHERE id = %s", (id,))
        result = self.cursor.fetchone()[0]
        if result == 0:
            return False
        elif result == 1:
            return True
        else:
            return None

    def day_exists(self, id):
        self.cursor.execute("SELECT COUNT (*) FROM forms WHERE id = %s", (id,))
        return self.cursor.fetchall()

    def get_form(self, id):
        self.cursor.execute("SELECT * FROM forms WHERE id = %s", (id,))
        return self.cursor.fetchall()

    def get_count(self, id):
        self.cursor.execute("SELECT count FROM users WHERE id = %s", (id,))
        return self.cursor.fetchone()[0]

    def get_user_id(self, user_id):
        self.cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    def get_photo_id(self, id):
        self.cursor.execute("SELECT user_id FROM users WHERE id = %s", (id,))
        return self.cursor.fetchone()[0]

    def get_username(self, id):
        self.cursor.execute("SELECT username FROM forms WHERE id = %s", (id,))
        return self.cursor.fetchone()[0]

    def get_username_by_id(self, username):
        self.cursor.execute("SELECT id FROM forms WHERE username = %s", (username,))
        return self.cursor.fetchone()[0]

    def get_user_liked(self, id):
        self.cursor.execute("SELECT liked FROM forms WHERE id = %s", (id,))
        return self.cursor.fetchone()[0]

    def get_noticed(self, banned_id):
        self.cursor.execute("SELECT noticed FROM ban WHERE id = %s", (banned_id,))
        return self.cursor.fetchone()[0]

    def get_user_claims(self, id):
        self.cursor.execute("SELECT claims FROM ban WHERE id = %s", (id,))
        return self.cursor.fetchone()[0]

    def add_user(self, id):
        self.cursor.execute("INSERT INTO users (id) VALUES (%s)", (id,))
        return self.conn.commit()

    def add_form(self, username, id, gender, interest, name, age, photo, text, liked):
        self.cursor.execute("INSERT INTO forms (username, id, name, age, photo, text, gender, interest, liked) \
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (username, id, name, age, photo, text, gender, interest, liked,))
        return self.conn.commit()

    def add_ban(self, id):
        self.cursor.execute("INSERT INTO ban (id) VALUES (%s)", (id,))
        return self.conn.commit()

    def update_text(self, id, new_text):
        self.cursor.execute("UPDATE forms SET text = %s WHERE id = %s", (new_text, id,))
        return self.conn.commit()

    def update_photo(self, id, photo_id):
        self.cursor.execute("UPDATE forms SET photo = %s WHERE id = %s", (photo_id, id,))
        return self.conn.commit()

    def update_liked(self, id, new_liked):
        self.cursor.execute("UPDATE forms SET liked = %s WHERE id = %s", (new_liked, id,))
        return self.conn.commit()

    def update_claims(self, id, new_claims):
        self.cursor.execute("UPDATE ban SET claims = %s WHERE id = %s", (new_claims, id,))
        self.cursor.execute("UPDATE ban SET count = count + 1 WHERE id = %s", (id,))
        self.cursor.execute("SELECT count FROM ban WHERE id = %s", (id,))
        if self.cursor.fetchone()[0] == 10:
            self.cursor.execute("UPDATE ban SET banned = true WHERE id = %s", (id,))
        return self.conn.commit()

    def update_noticed(self, id, new_noticed):
        self.cursor.execute("UPDATE ban SET noticed = %s WHERE id = %s", (new_noticed, id,))
        return self.conn.commit()

    def update_date(self, id, daily_views):
        self.cursor.execute("UPDATE users SET count = count+1 WHERE id = %s AND count <= %s", (id, daily_views,))
        self.cursor.execute("UPDATE users SET count = 1 WHERE id = %s AND ((NOW() - "
                            "(SELECT active_date FROM users WHERE id = %s) > interval '1 minute'))", (id, id,))
        self.cursor.execute("UPDATE users SET active_date = NOW() WHERE id = %s AND ((NOW() - "
                            "(SELECT active_date FROM users WHERE id = %s) > interval '1 minute'))", (id, id,))
        return self.conn.commit()

    def update_visible(self, id, status):
        self.cursor.execute("UPDATE ban SET visible = %s WHERE id = %s", (status, id,))
        return self.conn.commit()

    def delete_form(self, id):
        self.cursor.execute("DELETE FROM forms WHERE id = %s", (id,))
        return self.conn.commit()

    def delete_user(self, id):
        self.cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        return self.conn.commit()

    def find_forms(self, id, interest, age):
        gender: str = ""
        if interest == "парни":
            gender = "парень"
        if interest == "девушки":
            gender = "девушка"
        self.cursor.execute("SELECT * FROM forms"
                            " WHERE id != %s AND gender = %s AND age BETWEEN %s AND %s AND "
                            "id NOT IN (SELECT id FROM ban WHERE banned = True or visible = False)",
                            (id, gender, int(age) - 5, int(age) + 5))
        return self.cursor.fetchall()

    def find_banned(self):
        self.cursor.execute("SELECT * FROM forms WHERE id in (SELECT id FROM ban)")
        return self.cursor.fetchall()

    def ban_user(self, id):
        if not self.ban_exists(id):
            self.add_ban(id)
        self.cursor.execute("UPDATE ban SET banned = true WHERE id = %s", (id,))
        return self.conn.commit()

    def unban_user(self, id):
        self.cursor.execute("UPDATE ban SET banned = false WHERE id = %s", (id,))
        return self.conn.commit()

    def banned(self, id):
        self.cursor.execute("SELECT banned FROM ban WHERE id = %s", (id,))
        return self.cursor.fetchone()[0]

    def drop(self):
        self.cursor.execute("DELETE FROM forms")
        self.cursor.execute("DELETE FROM users")
        self.cursor.execute("DELETE FROM ban")
        self.cursor.execute("DROP TABLE users")
        self.cursor.execute("DROP TABLE forms")
        self.cursor.execute("DROP TABLE ban")
        self.create_table_users()
        self.create_table_forms()
        self.create_table_ban()
        return self.conn.commit()

    def close(self):
        self.conn.close()
