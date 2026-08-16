from dataclasses import dataclass
from datetime import datetime


@dataclass
class Author:
    id: int
    username: str

@dataclass
class Post:
    id: int
    author: Author
    title: str
    content: str
    date_posted: datetime | str

    def __post_init__(self):
        if isinstance(self.date_posted, str):
            self.date_posted = datetime.fromisoformat(
                self.date_posted
            )

