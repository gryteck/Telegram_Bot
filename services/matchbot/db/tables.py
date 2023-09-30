from db.schema import BotDB, db_exception


class BotDBTables(BotDB):
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
                    view_count SMALLINT DEFAULT 0 NOT NULL,
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
    def create_table_qrcodes(self):
        query = """CREATE TABLE qrcodes (
                        qr_id SMALLSERIAL PRIMARY KEY,
                        id BIGINT NOT NULL UNIQUE,
                        username TEXT,
                        name TEXT NOT NULL,
                        age SMALLINT NOT NULL,
                        gender TEXT NOT NULL,
                        join_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('Europe/Moscow', now()) NOT NULL,
                        active_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('Europe/Moscow', now()) NOT NULL,
                        visit_count SMALLINT DEFAULT 0 NOT NULL,
                        status TEXT NOT NULL,
                        promocode TEXT
                        );
                        CREATE INDEX qr_id_idx ON qrcodes (qr_id);"""
        self.cursor.execute(query)
        return self.conn.commit()

    @db_exception
    def create_table_visits(self):
        query = """CREATE TABLE visits (
                    visit_id SMALLSERIAL PRIMARY KEY,
                    date TIMESTAMP WITH TIME ZONE DEFAULT timezone('Europe/Moscow', now()) NOT NULL,
                    id BIGINT NOT NULL,
                    username TEXT,
                    name TEXT NOT NULL,
                    age SMALLINT NOT NULL,
                    gender TEXT NOT NULL,
                    visit_count SMALLINT DEFAULT 0 NOT NULL,
                    status TEXT NOT NULL,
                    promocode TEXT
                    );
                    """
        self.cursor.execute(query)
        return self.conn.commit()

    @db_exception
    def create_table_promocodes(self):
        query = """CREATE TABLE promocodes (
                    promocode_id SMALLSERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    join_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('Europe/Moscow', now()) NOT NULL,
                    active_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('Europe/Moscow', now()) NOT NULL,
                    visit_count SMALLINT DEFAULT 0 NOT NULL,
                    promocode TEXT
                    );
                    """
        self.cursor.execute(query)
        return self.conn.commit()

    @db_exception
    def table_users_exists(self):
        query = """SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');"""
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    @db_exception
    def table_qrcodes_exists(self):
        query = """SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'qrcodes');"""
        self.cursor.execute(query)
        return bool(self.cursor.fetchone()[0])

    @db_exception
    def table_visits_exists(self):
        query = """SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'visits');"""
        self.cursor.execute(query)
        return bool(self.cursor.fetchone()[0])

    @db_exception
    def table_promocodes_exists(self):
        query = """SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'promocodes');"""
        self.cursor.execute(query)
        return bool(self.cursor.fetchone()[0])

    @db_exception
    def drop_table_users(self):
        self.cursor.execute("DROP TABLE users")
        return self.conn.commit()

    @db_exception
    def drop_table_qrcodes(self):
        self.cursor.execute("DROP TABLE qrcodes")
        return self.conn.commit()

    @db_exception
    def drop_table_visits(self):
        self.cursor.execute("DROP TABLE visits")
        return self.conn.commit()

    @db_exception
    def drop_table_promocodes(self):
        self.cursor.execute("DROP TABLE promocodes")
        return self.conn.commit()


db_tables = BotDBTables()
