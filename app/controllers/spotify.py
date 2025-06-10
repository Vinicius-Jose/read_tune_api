from fastapi import APIRouter
from fastapi.responses import RedirectResponse
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
