import asyncpg
from src.config import db_url, db_url_local, db_url_docker, time, daily_views


class BotDB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(db_url)

    async def disconnect(self):
        await self.pool.close()

    async def create_table_users(self):
        async with self.pool.acquire() as conn:
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
                    liked TEXT NOT NULL,
                    join_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    active_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    view_count SMALLINT DEFAULT 0 NOT NULL,
                    claims_count SMALLINT DEFAULT 0 NOT NULL,
                    claims TEXT DEFAULT 0 NOT NULL,
                    banned BOOLEAN DEFAULT false NOT NULL,
                    noticed_users TEXT DEFAULT 0 NOT NULL,
                    visible BOOLEAN DEFAULT true NOT NULL
                    );
                    CREATE INDEX user_id_idx ON users (id);"""
            )
            await conn.execute(create_table)

    async def table_users_exists(self):
        async with self.pool.acquire() as conn:
            check_table = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'users'
                    );
                """
            return await conn.fetchval(check_table)

    async def user_exists(self, id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("SELECT user_id FROM users WHERE id = %s", (id,))
            return bool(len(conn.fetchall()))

    async def get_form(self, id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetch("SELECT * FROM forms WHERE id = %s", (id,))

            if row is None:
                return {}
            else:
                column_names = [desc[0] for desc in conn.description]
                user_data = {}
                for i in range(len(column_names)):
                    user_data[column_names[i]] = row[i]
                return user_data

    async def get_noticed(self, id: int):
        async with self.pool.acquire() as conn:
            result = await conn.fetch("SELECT noticed_users FROM forms WHERE id = %s", (id,))
            return result[0]

    async def post_user(self, username: str, id: int, gender: str, interest: str, name: str, age: int, photo: str,
                        text: str):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO users (username, id, name, age, photo, text, gender, interest, liked) "
                               "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                               (username, id, name, age, photo, text, gender, interest, "0"))

    async def patch_user(self, id: int, gender: str, interest: str, name: str, age: int, photo: str, text: str):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET name = %s, gender = %s, interest = %s, age = %s, photo = %s, text = %s"
                               " WHERE id = %s", (name, gender, interest, age, photo, text, id,))

    async def patch_visible(self, id: int, visible: bool):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET visible = %s WHERE id = %s", (visible, id,))

    async def patch_text(self, id: int, text: str):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET text = %s WHERE id = %s", (text, id,))

    async def patch_liked(self, id: int, liked: str):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET liked = %s WHERE id = %s", (liked, id,))
            return liked

    async def patch_photo(self, id: int, photo: str):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET photo = %s WHERE id = %s", (photo, id,))

    async def patch_claims(self, id: int, noticed: str, claims: str):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET noticed_users = %s, claims = %s WHERE id = %s", (noticed, claims, id,))

    async def get_random_user(self, id: int, age: int, interest: str):
        async with self.pool.acquire() as conn:
            if interest == 'парни':
                row = await conn.fetch("SELECT * FROM users WHERE id != %s AND age BETWEEN %s AND %s "
                                       "AND gender = 'парень' AND banned = false AND visible = true "
                                       "ORDER BY RANDOM() LIMIT 1",
                                       (id, age - 2, age + 5))
            else:
                row = await conn.fetch("SELECT * FROM forms WHERE id != %s AND age BETWEEN %s AND %s "
                                       "AND gender = 'девушка' AND banned = false AND visible = true "
                                       "ORDER BY RANDOM() LIMIT 1",
                                       (id, age - 5, age + 2))
            await conn.execute("UPDATE users SET view_count = view_count+1 WHERE id = %s", (id, daily_views,))
            await conn.execute("UPDATE users SET view_count = 1 WHERE id = %s AND ((NOW() - "
                               "(SELECT active_date FROM users WHERE id = %s) > interval %s))", (id, id, time,))
            await conn.execute("UPDATE users SET active_date = NOW() WHERE id = %s AND ((NOW() - "
                               "(SELECT active_date FROM users WHERE id = %s) > interval %s))", (id, id, time,))
            if row is None:
                return {}
            else:
                column_names = [desc[0] for desc in conn.description]
                user_data = {}
                for i in range(len(column_names)):
                    user_data[column_names[i]] = row[i]
                return user_data
