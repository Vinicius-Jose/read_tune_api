from typing import TypedDict, Annotated
from operator import add

from app.models.models import Playlist


class OverallState(TypedDict):
    book_id: str
    book_title: str
    book_authors: str
    isbn: str
    context: Annotated[list, add]
    max_songs: int
    min_songs: int
    category: str
    playlist_style: str


class OutputState(TypedDict):
    playlist: Playlist
