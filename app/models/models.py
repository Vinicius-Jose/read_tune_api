from typing import Optional
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField


class Style(BaseModel):
    name: str = Field(description="Name of the style")
    description: str = Field(description="Description of the style")


class Song(BaseModel):
    artist_name: str = Field(description="Name of the singer")
    song_name: str = Field(description="Name of the song")


class Playlist(BaseModel):
    name: str = Field(
        description="The name of the playlist. Must include the book name, book author,"
        " isbn and the name of style you receive "
        "must be in the following style Book Name - Book Author - ISBN - Style "
    )
    description: str = Field(
        description="A little description about the playlist with no more than 50 words"
    )
    song_list: list[Song] = Field(description="List of songs in playlist")


class PlaylistResponse(BaseModel):
    id: str = Field(description="Id playlist on spotify")
    link: str = Field(description="Link to open spotify playlist")


class BookResponse(BaseModel):
    volume_id: str = Field(description="Volume ID")
    title: str = Field(description="Title of the volume/book")
    authors: list[str] = Field(description="List of authors")
    description: str = Field(description="Description of the volume")
    isbn: str = Field(description="ISBN 13")
    categories: Optional[list[str]] = Field(description="Categories")
    thumbnail: Optional[str] = Field(description="URL with the tumbnail")
    language: str = Field(description="Language")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(SQLModel, table=True):
    username: str = SQLField(nullable=False)
    email: str = SQLField(nullable=False, primary_key=True)
    full_name: str = SQLField(nullable=False)
    password: str = SQLField(nullable=False)
    admin: bool = SQLField(nullable=False, default=False)
