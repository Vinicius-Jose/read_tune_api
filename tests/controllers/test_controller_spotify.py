from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_spotify_login() -> None:
    response = client.get("spotify/login", follow_redirects=False)
    assert response.has_redirect_location
    assert "https://accounts.spotify.com/authorize" in response.headers.get("location")


def test_spotify_playlist() -> None:
    response = client.get("spotify/playlist")
    assert response.status_code == 200
    response = response.json()
    assert isinstance(response, list)
    assert response[0].get("id")
