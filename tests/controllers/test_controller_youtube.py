from fastapi.testclient import TestClient
from app.main import app
from tests.test_main import authenticate
import os

client = TestClient(app)


def test_youtube_playlist() -> None:
    headers = authenticate(os.environ["EMAIL_ADMIN"], os.environ["PWD_ADMIN"])
    response = client.get("youtube/playlist", headers=headers)
    assert response.status_code == 200
    response = response.json()
    assert isinstance(response, list)
    assert response[0].get("id")
