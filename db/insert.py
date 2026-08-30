#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path

from db.base import Database
from db.models import User, Post


BASE_DIR = Path(__file__).parent.parent

db = Database(BASE_DIR / "new.db")

User.db = db
Post.db = db

User.create_table()
Post.create_table()


john = User.create(
    username="John Doe",
    image_path="/static/profile_pic/default.jpg",
)

jane = User.create(
    username="Jane Doe",
    image_path="/static/profile_pic/default.jpg",
)

Post.create(
    author_id=john.id,
    title="Post 1",
    content="This is the content of my first post.",
    date_posted=datetime(1999, 12, 31).isoformat(),
)

Post.create(
    author_id=jane.id,
    title="Post 2",
    content="This is the content of my second post.",
    date_posted=datetime(2000, 1, 1).isoformat(),
)

