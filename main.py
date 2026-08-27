#!/usr/bin/env python3

import logging
from pathlib import Path
from pprint import pformat

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
app.file_mounts["/static/"] = (BASE_DIR / "static")
app.file_mounts["/media/"] = (BASE_DIR / "media")

@app.get("/")
async def home(request):
	posts = db.get_posts()
	return template.response(
		"home.html",
		title="what up!",
		url_for=app.url_for,
		posts=posts,
	)

@app.post("/create_user")
async def create_user(request):
	# DEBUG:
	# return f"""
	# 	{request.headers.get("Content-Type")}
	# 	{request.form()}
	# 	{request.body.decode()}
	# """
	username = request.form().get("username", "").strip()
	if not username:
		return "Username is required"
	if db.username_exists(username):
		return f"Username {username} already exists"
	user_id = db.insert_user(
		username=username,
		image_path="/static/profile_pic/default.jpg"
	)
	return f"Created user {user_id}: {username}"

@app.get("/users/{user_id}")
async def user_post_page(request, user_id):
	return f"User {user_id}"

@app.get("/posts/{post_id}")
async def post_page(request, post_id):
	return f"Post {post_id}"

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=8080)

