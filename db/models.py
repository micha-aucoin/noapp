from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    image_path: str


@dataclass
class Post:
    id: int
    author: User
    title: str
    content: str
    date_posted: datetime

