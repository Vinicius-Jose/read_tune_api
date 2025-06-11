from dotenv import load_dotenv
from app.services.spotify import SpotifyAPI

load_dotenv("./.env")


def test_get_token() -> None:
    spotify = SpotifyAPI()
    response = spotify.get_token()
    assert isinstance(response, dict)


def test_search_track() -> None:
    spotify = SpotifyAPI()
    track_search = "We are the champions"
    artist_search = "Queen"
    response = spotify.search(f"{track_search} {artist_search}", search_type=["track"])
    assert isinstance(response, dict)
    tracks = response["tracks"]
    items = tracks["items"]
    track = items[0]
    track_name = track["name"]
    track_artist = track["artists"][0]["name"]
    assert track_search.lower() in track_name.lower()
    assert artist_search.lower() in track_artist.lower()


def test_get_current_user() -> None:
    spotify = SpotifyAPI()
    response = spotify.get_current_user()
    assert isinstance(response, dict)
    assert response["id"]


def test_create_playlist() -> None:
    spotify = SpotifyAPI()
    user = spotify.get_current_user()
    user_id = user["id"]
    playlist_name = "Test Playlist"
    playlist_description = "This is a test playlist"
    response = spotify.create_playlist(
        user_id=user_id,
        name=playlist_name,
        description=playlist_description,
        public=False,
    )
    assert isinstance(response, dict)
    assert response["name"] == playlist_name
    assert response["description"] == playlist_description
    assert response["owner"]["id"] == user_id
    spotify.unfollow_playlist(response["id"])


def test_create_and_add_tracks_playlist() -> None:
    tracks_uris = []
    spotify = SpotifyAPI()
    user_id = spotify.get_current_user()["id"]
    playlist_name = "Test"
    description = "Test create and add tracks"
    response_playlist = spotify.create_playlist(
        user_id=user_id,
        name=playlist_name,
        description=description,
        public=False,
    )
    search_response = spotify.search("We are the champions", search_type=["track"])
    tracks_uris.append(search_response["tracks"]["items"][0]["uri"])
    search_response = spotify.search("Rabbit Run Eminem", search_type=["track"])
    tracks_uris.append(search_response["tracks"]["items"][0]["uri"])
    response = spotify.add_tracks_to_playlist(
        playlist_id=response_playlist["id"], tracks_uris=tracks_uris
    )
    assert isinstance(response, dict)
    assert response["snapshot_id"]
    spotify.unfollow_playlist(response_playlist["id"])


def test_search_playlist() -> None:
    spotify = SpotifyAPI()
    playlist_name = "Lofi Girl - beats to relax/study to"
    response = spotify.search(playlist_name, search_type=["playlist"])
    assert isinstance(response, dict)
    playlists = response["playlists"]
    items = playlists["items"]
    assert items[0]["name"] == playlist_name


def test_get_playlist() -> None:
    spotify = SpotifyAPI()
    playlist_id = "741HfcYMK871cpb3gNXBs9"
    response = spotify.get_playlist(playlist_id)
    assert response.get("name")


def test_get_playlists_user() -> None:
    spotify = SpotifyAPI()
    user = spotify.get_current_user()
    user_id = user["id"]
    response = spotify.get_playlists_user(user_id)
    assert isinstance(response.get("items"), list)
