from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.models.models import PlaylistResponse
from app.services.spotify import SpotifyAPI


router = APIRouter(
    prefix="/spotify",
    tags=["spotify"],
)


@router.get("/login")
def spotify_login():
    spotify = SpotifyAPI()
    return RedirectResponse(spotify.get_url_login())


@router.get("/callback")
def spotify_callback(code: str):
    spotify = SpotifyAPI()
    token = spotify.get_token(code)
    return {"token": token}


@router.get("/playlist")
def spotify_playlist() -> list[PlaylistResponse]:
    spotify = SpotifyAPI()
    user = spotify.get_current_user()
    user_id = user["id"]
    response = spotify.get_playlists_user(user_id)
    playlists = []
    for item in response["items"]:
        playlist = PlaylistResponse(
            id=item.get("id"), link=item["external_urls"]["spotify"]
        )
        playlists.append(playlist)
    return playlists
