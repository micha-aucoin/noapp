import sqlite3
from pathlib import Path
from datetime import datetime

from .models import Post, User

BASE_DIR = Path(__file__).parent.parent

class Database:
    def __init__(self, path=(BASE_DIR / "app.db")):
        self.path = path

    def connect(self) -> None:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def create_tables(self) -> None:
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    image_path TEXT NOT NULL
                )
            """)
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

    def get_user(self, user_id: id) -> None | User:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return User(
            id=row["id"],
            username=row["username"],
            image_path=row["image_path"],
        )

    def get_post(self, post_id: id) -> None | Post:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    posts.id,
                    posts.title,
                    posts.content,
                    posts.date_posted,
                    users.id AS user_id,
                    users.username,
                    users.image_path
                FROM posts
                JOIN users
                    ON users.id = posts.author_id
                WHERE posts.id = ?
                """,
                (post_id,),
            ).fetchone()
        if row is None:
            return None
        return Post(
            id=row["id"],
            author=User(
                id=row["user_id"],
                username=row["username"],
                image_path=row["image_path"],
            ),
            title=row["title"],
            content=row["content"],
            date_posted=datetime.fromisoformat(row["date_posted"]),
        )

    def insert_user(self, username: str, image_path: str) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (username, image_path)
                VALUES (?, ?)
                """,
                (username, image_path),
            )
        return cursor.lastrowid

    def insert_post(
        self,
        author_id: int,
        title: str,
        content: str,
        date_posted: str,
    ) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO posts (author_id, title, content, date_posted)
                VALUES (?, ?, ?, ?)
                """,
                (author_id, title, content, date_posted),
            )
        return cursor.lastrowid

    def get_posts(self) -> list[Post]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    posts.id,
                    posts.title,
                    posts.content,
                    posts.date_posted,

                    users.id AS user_id,
                    users.username,
                    users.image_path

                FROM posts
                JOIN users
                    ON users.id = posts.author_id

                ORDER BY posts.id
                """
            ).fetchall()

        posts = []
        for row in rows:
            user = User(
                id=row["user_id"],
                username=row["username"],
                image_path=row["image_path"],
            )
            post = Post(
                id=row["id"],
                author=user,
                title=row["title"],
                content=row["content"],
                date_posted=datetime.fromisoformat(row["date_posted"]),
            )
            posts.append(post)
        return posts

    def username_exists(self, username: str) -> bool:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return row is not None
