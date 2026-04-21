from dotenv import load_dotenv
from app.services.youtube import YoutubeAPI
import os

load_dotenv("./.env")


def test_get_url_login() -> None:
    youtube = YoutubeAPI()
    response = youtube.get_url_login()
    assert isinstance(response, str)


def test_get_refresh_token() -> None:
    youtube = YoutubeAPI()
    response = youtube.get_url_login()
    code = ""
    credentials = youtube.get_refresh_token(code=code)
    credentials = credentials.to_json()
    with open(os.environ.get("GOOGLE_TOKEN_JSON_FILE"), "w") as token_file:
        token_file.write(credentials)
    assert isinstance(credentials, str)


def test_search() -> None:
    youtube = YoutubeAPI()
    response = youtube.search(query="test")
    assert len(response) > 0
    assert response[0].content_id


def test_get_current_user() -> None:
    youtube = YoutubeAPI()
    user_id = youtube.get_current_user()
    assert user_id


def test_create_playlist() -> None:
    youtube = YoutubeAPI()
    response = youtube.create_playlist(0, "Test", "Test for api")
    assert response.id
    youtube.unfollow_playlist(response.id)


def test_add_tracks_to_playlist() -> None:
    youtube = YoutubeAPI()
    response = youtube.create_playlist(0, "Test", "Test for api")
    playlist_id = response.id
    assert playlist_id
    video = youtube.search(query="Eminem Lose yourself", limit=1)
    video = video[0].content_id
    response = youtube.add_tracks_to_playlist(playlist_id, video)
    assert response.get("id")
    youtube.unfollow_playlist(playlist_id)


def test_get_playlist() -> None:
    youtube = YoutubeAPI()
    playlist_id = "PLRgSHCeagEV5xIPwkev2WD3D0Dz9AUXcj"
    response = youtube.get_playlist(playlist_id)
    assert response.get("items", [{}])[0].get("id")


def test_get_playlists_user() -> None:
    youtube = YoutubeAPI()
    user_id = "UCfM3zsQsOnfWNUppiycmBuw"
    response = youtube.get_playlists_user(user_id=user_id)
    assert len(response) > 0
