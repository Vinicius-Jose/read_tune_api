from time import sleep
from app.controllers.llm import get_volume_google_books, save_playlist
from fastapi.testclient import TestClient
from app.main import app
from app.models.models import Playlist, Song
from app.services.spotify import SpotifyAPI
import pytest

client = TestClient(app)


def test_get_volume_google_books() -> None:
    volume_id = "HB-OEAAAQBAJ"
    response = get_volume_google_books(volume_id)
    title = "The End of Eternity"
    title_response: str = response["book_title"]
    assert title.lower() == title_response.lower()


def test_save_playlist() -> None:
    song_list = [
        Song(artist_name="Queen", song_name="We are the Champions"),
        Song(artist_name="Eminem", song_name="Forever"),
        Song(artist_name="Bruno Mars", song_name="Uptown Funk"),
        Song(artist_name="Anderson .Paak", song_name="Put me Thru"),
    ]
    playlist = Playlist(
        name="Test Playlist", description="Test from save playlist", song_list=song_list
    )
    api = SpotifyAPI()
    response = save_playlist(playlist=playlist, api=api)
    assert response.id
    assert response.link
    playlist_search = api.get_playlist(response.id)
    assert playlist_search["name"] == playlist.name
    assert playlist_search["tracks"]["total"] == len(song_list)
    api.unfollow_playlist(response.id)


@pytest.mark.parametrize(
    "playlist_style, min_songs, max_songs",
    [("", 1, 2), ("Classical", 1, 2), ("Lo-Fi", 1, 2), ("Electronic/Chillwave", 3, 5)],
)
def test_get_playlist(playlist_style: str, min_songs: str, max_songs: int) -> None:
    volume_id = "HB-OEAAAQBAJ"
    params = {
        "playlist_style": playlist_style,
        "min_songs": min_songs,
        "max_songs": max_songs,
    }
    response = client.get(f"/llm/{volume_id}", params=params)
    assert response.status_code == 200
