# tests/test_db.py

import sqlite3
import unittest

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from db.base import CRUD, Database
from db.models import User, Post


class TestDatabaseAPI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"

        self.db = Database(self.db_path)

        User.db = self.db
        Post.db = self.db

        User.create_table()
        Post.create_table()

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_user(self, username="John"):
        return User.create(
            username=username,
            image_path="/static/profile_pic/default.jpg",
        )

    def create_post(
        self,
        author,
        title="First Post",
        content="Hello World",
    ):
        return Post.create(
            author_id=author.id,
            title=title,
            content=content,
            date_posted=datetime(2000, 1, 1).isoformat(),
        )

    def test_create_user(self):
        user = self.create_user()

        self.assertIsInstance(user, User)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "John")
        self.assertEqual(
            user.image_path,
            "/static/profile_pic/default.jpg",
        )

    def test_read_user(self):
        created_user = self.create_user()

        user = User.read(created_user.id)

        self.assertIsInstance(user, User)
        self.assertEqual(user.id, created_user.id)
        self.assertEqual(user.username, "John")

    def test_read_missing_user_returns_none(self):
        user = User.read(999)

        self.assertIsNone(user)

    def test_update_user(self):
        user = self.create_user()

        updated_user = User.update(
            user.id,
            username="Jane",
        )

        self.assertEqual(updated_user.id, user.id)
        self.assertEqual(updated_user.username, "Jane")

    def test_delete_user(self):
        user = self.create_user()

        User.delete(user.id)

        self.assertIsNone(User.read(user.id))

    def test_all(self):
        self.create_user("John")
        self.create_user("Jane")

        users = User.all()

        self.assertEqual(len(users), 2)
        self.assertTrue(
            all(isinstance(user, User) for user in users)
        )

    def test_all_returns_empty_list(self):
        users = User.all()

        self.assertEqual(users, [])

    def test_filter(self):
        self.create_user("John")
        self.create_user("Jane")

        users = User.filter(username="Jane")

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, "Jane")

    def test_filter_multiple_conditions(self):
        User.create(
            username="John",
            image_path="/john.jpg",
        )
        User.create(
            username="Jane",
            image_path="/jane.jpg",
        )

        users = User.filter(
            username="Jane",
            image_path="/jane.jpg",
        )

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, "Jane")

    def test_filter_no_match_returns_empty_list(self):
        self.create_user("John")

        users = User.filter(username="Nobody")

        self.assertEqual(users, [])

    def test_filter_without_arguments_returns_all(self):
        self.create_user("John")
        self.create_user("Jane")

        users = User.filter()

        self.assertEqual(len(users), 2)

    def test_create_post(self):
        user = self.create_user()

        post = self.create_post(user)

        self.assertIsInstance(post, Post)
        self.assertIsNotNone(post.id)
        self.assertEqual(post.author_id, user.id)
        self.assertEqual(post.title, "First Post")

    def test_post_date_is_converted_to_datetime(self):
        user = self.create_user()

        post = self.create_post(user)

        self.assertIsInstance(
            post.date_posted,
            datetime,
        )

    def test_post_author(self):
        user = self.create_user()
        post = self.create_post(user)

        author = post.author

        self.assertIsInstance(author, User)
        self.assertEqual(author.id, user.id)
        self.assertEqual(author.username, "John")

    def test_filter_posts_by_author(self):
        john = self.create_user("John")
        jane = self.create_user("Jane")

        self.create_post(john, title="John Post 1")
        self.create_post(john, title="John Post 2")
        self.create_post(jane, title="Jane Post")

        posts = Post.filter(author_id=john.id)

        self.assertEqual(len(posts), 2)
        self.assertTrue(
            all(post.author_id == john.id for post in posts)
        )

    def test_missing_table_name_raises_error(self):
        class Model(CRUD):
            db = self.db

        with self.assertRaises(ValueError):
            Model.all()

    def test_missing_database_raises_error(self):
        class Model(CRUD):
            table_name = "things"

        with self.assertRaises(RuntimeError):
            Model.all()

    def test_create_table_must_be_implemented(self):
        class Model(CRUD):
            table_name = "things"
            db = self.db

        with self.assertRaises(NotImplementedError):
            Model.create_table()

    def test_from_row_must_be_implemented(self):
        class Model(CRUD):
            table_name = "things"
            db = self.db

        with self.assertRaises(NotImplementedError):
            Model.from_row({})


class TestSession(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.db = Database(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_session_commits(self):
        with self.db.session() as connection:
            connection.execute(
                "CREATE TABLE things (id INTEGER)"
            )
            connection.execute(
                "INSERT INTO things (id) VALUES (?)",
                (1,),
            )

        with self.db.session() as connection:
            row = connection.execute(
                "SELECT id FROM things"
            ).fetchone()

        self.assertEqual(row["id"], 1)

    def test_session_rolls_back_on_exception(self):
        with self.db.session() as connection:
            connection.execute(
                "CREATE TABLE things (id INTEGER)"
            )

        try:
            with self.db.session() as connection:
                connection.execute(
                    "INSERT INTO things (id) VALUES (?)",
                    (1,),
                )
                raise ValueError("fail")
        except ValueError:
            pass

        with self.db.session() as connection:
            row = connection.execute(
                "SELECT id FROM things"
            ).fetchone()

        self.assertIsNone(row)


if __name__ == "__main__":
    unittest.main(verbosity=2)
