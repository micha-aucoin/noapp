from datetime import datetime
from .base import CRUD


class User(CRUD):
    table_name = "users"

    def __init__(self, id, username, image_path):
        self.id = id
        self.username = username
        self.image_path = image_path

    def __repr__(self):
        return (
            f"User(id={self.id}, "
            f"username={self.username}, "
            f"image_path={self.image_path})"
        )

    @classmethod
    def username_exists(cls, username):
        cls._check_config()
        with cls.db.session() as connection:
            row = connection.execute(
                f"SELECT 1 FROM {cls.table_name} WHERE username = ?",
                (username,),
            ).fetchone()
        return row is not None

    @classmethod
    def create_table(cls):
        cls._check_config()
        with cls.db.session() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    image_path TEXT NOT NULL
                )
            """)

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            username=row["username"],
            image_path=row["image_path"],
        )


class Post(CRUD):
    table_name = "posts"

    def __init__(self, id, author_id, title, content, date_posted):
        self.id = id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.date_posted = date_posted

    def __repr__(self):
        return (
            f"Post(id={self.id}, "
            f"author_id={self.author_id}, "
            f"title={self.title}, "
            f"content={self.content}, "
            f"date_posted={self.date_posted})"
        )

    @property
    def author(self):
        return User.read(self.author_id)

    @classmethod
    def create_table(cls):
        cls._check_config()
        with cls.db.session() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    author_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    date_posted TEXT NOT NULL,
                    FOREIGN KEY (author_id) REFERENCES users(id)
                )
            """)

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            author_id=row["author_id"],
            title=row["title"],
            content=row["content"],
            date_posted=datetime.fromisoformat(row["date_posted"]),
        )

