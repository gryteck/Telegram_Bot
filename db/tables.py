import psycopg2
from src.config import db_url, db_url_local, db_url_docker, time, daily_views
from db.schema import BotDB


class BotDBTables(BotDB):
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
        self.cursor.execute(create_table)
        return self.conn.commit()

    def table_users_exists(self):
        query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'users'
                    );
                """
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]