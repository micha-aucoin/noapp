#!/usr/bin/env python3

import time
import logging
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from noapp import App, Template
from db.base import Database


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

db = Database()

BASE_DIR = Path(__file__).parent
template = Template(directory=(BASE_DIR / "templates"))

app = App()
app.mount(path="/static/", directory=(BASE_DIR / "static"))
app.mount(path="/media/", directory=(BASE_DIR / "media"))

@app.get("/index")
async def index(request):
    return template.response(
        "layout.html",
    )

@app.get("/")
async def home(request):
    posts = db.get_posts()
    return template.response(
        "home.html",
        title="what up!",
        url_for=app.url_for,
        posts=posts,
    )

@app.get("/users/{user_id}")
async def user_post_page(request, user_id):
    return f"User {user_id}"

@app.get("/posts/{post_id}")
async def post_page(request, post_id):
    return f"Post {post_id}"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)

