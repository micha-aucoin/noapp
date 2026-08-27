#!/usr/bin/env python3

from base import Database


db = Database()
db.create_tables()

john_id = db.insert_user(
    username="John Doe",
    image_path="/static/profile_pic/defult.jpg",
)

jane_id = db.insert_user(
    username="Jane Doe",
    image_path="/static/profile_pic/defult.jpg",
)

db.insert_post(
    author_id=john_id,
    title="Post 1",
    content="This is the content of my first post.",
    date_posted="1999-12-31T00:00:00",
)

db.insert_post(
    author_id=jane_id,
    title="Post 2",
    content="This is the content of my second post.",
    date_posted="2000-01-01T00:00:00",
)

