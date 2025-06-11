from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv
import pytest
import os

load_dotenv("./.env")
client = TestClient(app)


@pytest.mark.parametrize(
    "email, pwd",
    [
        (os.environ["EMAIL_ADMIN"], os.environ["PWD_ADMIN"]),
        (os.environ["EMAIL_CLIENT"], os.environ["PWD_CLIENT"]),
    ],
)
def test_token(email: str, pwd: str) -> None:
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = f"grant_type=password&username={email}&password={pwd}"
    response = client.post("/token", data=payload, headers=headers)
    assert response.status_code == 200
    response = response.json()
    assert response["access_token"]
    assert response["token_type"] == "Bearer"


def authenticate(email: str, pwd: str):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = f"grant_type=password&username={email}&password={pwd}"
    response = client.post("/token", data=payload, headers=headers)
    response = response.json()
    return {"Authorization": f"{response['token_type']} {response['access_token']}"}


def test_full_execution() -> None:
    headers = authenticate(os.environ["EMAIL_ADMIN"], os.environ["PWD_ADMIN"])
    title = "The end of eternity"
    playlist_style = "Jazz"
    max_results = 2
    min_songs = 2
    max_songs = 4
    params = {"query": title, "max_results": max_results}
    response = client.get("books/", params=params, headers=headers)
    assert response.status_code == 200
    volumes = response.json()
    assert len(volumes) <= max_results and len(volumes) > 0
    volume: dict = volumes[0]
    assert title.lower() in volume.get("title").lower()
    volume_id = volume.get("volume_id")
    params = {
        "playlist_style": playlist_style,
        "min_songs": min_songs,
        "max_songs": max_songs,
    }
    response = client.get(f"/llm/{volume_id}", params=params, headers=headers)
    assert response.status_code == 200
    playlist = response.json()
    assert playlist.get("id")
    assert playlist.get("link")
