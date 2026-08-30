import sqlite3

class Session:
    def __init__(self, path):
        self.path = path
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.connection.close()


class Database:
    def __init__(self, path):
        self.path = path

    def session(self):
        return Session(self.path)


class CRUD:
    table_name = ""
    db = None

    @classmethod
    def _check_config(cls):
        if not cls.table_name:
            raise ValueError(f"{cls.__name__}.table_name must be set")
        if cls.db is None:
            raise RuntimeError(f"{cls.__name__}.db must be set")

    @classmethod
    def create(cls, **kwargs):
        cls._check_config()
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join("?" for _ in kwargs)
        sql = (
            f"INSERT INTO {cls.table_name} "
            f"({columns}) VALUES ({placeholders})"
        )
        parameters = tuple(kwargs.values())
        with cls.db.session() as connection:
            cursor = connection.execute(sql, parameters)
            row_id = cursor.lastrowid
        return cls.read(row_id)

    @classmethod
    def read(cls, row_id):
        cls._check_config()
        sql = f"SELECT * from {cls.table_name} WHERE id = ?"
        parameters = (row_id,)
        with cls.db.session() as connection:
            cursor = connection.execute(sql, parameters)
            row = cursor.fetchone()
            if row is None:
                return None
            return cls.from_row(row)

    @classmethod
    def update(cls, row_id, **kwargs):
        cls._check_config()
        assignments = ", ".join(
            f"{column} = ?" for column in kwargs
        )
        sql = (
            f"UPDATE {cls.table_name} "
            f"SET {assignments} "
            f"WHERE id = ?"
        )
        parameters = tuple(kwargs.values()) + (row_id,)
        with cls.db.session() as connection:
            connection.execute(sql, parameters)
        return cls.read(row_id)

    @classmethod
    def delete(cls, row_id):
        cls._check_config()
        sql = f"DELETE FROM {cls.table_name} WHERE id = ?"
        parameters = (row_id,)
        with cls.db.session() as connection:
            connection.execute(sql, parameters)

    @classmethod
    def all(cls):
        cls._check_config()
        sql = f"SELECT * FROM {cls.table_name}"
        with cls.db.session() as connection:
            rows = connection.execute(sql).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def filter(cls, **kwargs):
        cls._check_config()
        if not kwargs:
            return cls.all()
        conditions = " AND ".join(
            f"{column} = ?" for column in kwargs
        )
        sql = (
            f"SELECT * FROM {cls.table_name} "
            f"WHERE {conditions}"
        )
        parameters = tuple(kwargs.values())
        with cls.db.session() as connection:
            rows = connection.execute(sql, parameters).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def from_row(cls, row):
        raise NotImplementedError

    @classmethod
    def create_table(cls):
        raise NotImplementedError

