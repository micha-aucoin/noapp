#!/usr/bin/env python3

import logging
from pathlib import Path
from noapp import App, Template
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s", 
)

@dataclass
class Author:
    id: int
    username: str
    image_path: str


@dataclass
class Post:
    id: int
    author: Author
    title: str
    content: str
    date_posted: datetime

authors = [
    Author(id=1, username="John Doe", image_path="/static/profile_pic/defult.jpg"),
    Author(id=2, username="Jane Doe", image_path="/static/profile_pic/defult.jpg"),
]

posts = [
    Post(
        id=1,
        author=authors[0],
        title="Post 1",
        content="This is the content of my first post.",
        date_posted=datetime(1999, 12, 31),
    ),
    Post(
        id=2,
        author=authors[1],
        title="Post 2",
        content="This is the content of my second post.",
        date_posted=datetime(2000, 1, 1),
    ),
    Post(
        id=3,
        author=authors[0],
        title="Post 3",
        content="This is the content of my third post.",
        date_posted=datetime(2000, 1, 2),
    ),
]

templates_dir = Path(__file__).parent / "templates"
template = Template(directory=templates_dir)
app = App()

@app.get("/index")
async def index():
    return template.response(
        "layout.html",
        title="what up!",
        heading="Hello, World!",
        url_for=app.url_for,
    )

@app.get("/")
async def home():
    return template.response(
        "home.html",
        title="what up!",
        url_for=app.url_for,
        posts=posts,
    )

@app.get("/users/{user_id}")
async def user_post_page(user_id):
    return f"User {user_id}"

@app.get("/posts/{post_id}")
async def post_page(post_id):
    return f"Post {post_id}"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)

