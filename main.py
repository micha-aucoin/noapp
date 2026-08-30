#!/usr/bin/env python3

import logging
from datetime import datetime
from pathlib import Path
from pprint import pformat

from noapp import App, Template, Response
from db.base import Database
from db.models import User, Post


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


BASE_DIR = Path(__file__).parent

template = Template(directory=(BASE_DIR / "templates"))

app_db = Database(path=(BASE_DIR / "app.db"))
User.db = app_db
User.create_table()
Post.db = app_db
Post.create_table()

app = App()
app.file_mounts["/static/"] = (BASE_DIR / "static")
app.file_mounts["/media/"] = (BASE_DIR / "media")

@app.get("/")
async def home(request):
    response = Response()
    posts = Post.all()
    html = template.response(
        "home.html",
        title="what up!",
        url_for=app.url_for,
        posts=posts,
    )
    return response.html(html)

@app.post("/create_user")
async def create_user(request):
	# DEBUG:
	# return f"""
	# 	{request.headers.get("Content-Type")}
	# 	{request.form()}
	# 	{request.body.decode()}
	# """
    response = Response()
    username = request.form().get("username", "").strip()
    if not username:
        return response.text("Username is required")
    if User.username_exists(username):
        return response.text(f"Username {username} already exists")
    user = User.create(
        username=username,
        image_path="/static/profile_pic/default.jpg"
    )
    return response.text(f"Created user {user.id}: {user.username}")

@app.get("/posts/create")
async def create_post_page(request):
    response = Response()
    html = template.response(
        "create_post.html",
        title="Create Post",
        url_for=app.url_for,
    )
    return response.html(html)

@app.post("/posts/create")
async def create_post(request):
    response = Response()
    form = request.form()
    author_id = form.get("author_id", "").strip()
    title = form.get("title", "").strip()
    content = form.get("content", "").strip()

    if not author_id:
        return response.text("Author is required")
    if not title:
        return response.text("Title is required")
    if not content:
        return response.text("Content is required")

    author = User.read(int(author_id))
    if author is None:
        return response.text("User does not exist")

    post = Post.create(
        author_id=author.id,
        title=title,
        content=content,
        date_posted=datetime.now().isoformat(),
    )
    return response.redirect("/")

@app.get("/users/{user_id}")
async def user_post_page(request, user_id):
	return f"User {user_id}"

@app.get("/posts/{post_id}")
async def post_page(request, post_id):
	return f"Post {post_id}"

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=8080)

