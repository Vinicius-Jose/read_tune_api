from fastapi.testclient import TestClient
from app.main import app
from tests.test_main import authenticate
import os

client = TestClient(app)


def test_spotify_login() -> None:
    headers = authenticate(os.environ["EMAIL_ADMIN"], os.environ["PWD_ADMIN"])
    response = client.get("spotify/login", follow_redirects=False, headers=headers)
    assert response.has_redirect_location
    assert "https://accounts.spotify.com/authorize" in response.headers.get("location")


def test_spotify_login_forbidden() -> None:
    headers = authenticate(os.environ["EMAIL_ADMIN"], os.environ["PWD_ADMIN"])
    os.environ["ENVIRONMENT"] = "production"
    response = client.get("spotify/login", follow_redirects=False, headers=headers)
    assert response.status_code == 403


def test_spotify_playlist() -> None:
    headers = authenticate(os.environ["EMAIL_ADMIN"], os.environ["PWD_ADMIN"])
    response = client.get("spotify/playlist", headers=headers)
    assert response.status_code == 200
    response = response.json()
    assert isinstance(response, list)
    assert response[0].get("id")


def test_spotify_playlist_not_allowed() -> None:
    headers = authenticate(os.environ["EMAIL_CLIENT"], os.environ["PWD_CLIENT"])
    response = client.get("spotify/playlist", headers=headers)
    assert response.status_code == 405
