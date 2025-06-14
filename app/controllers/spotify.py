from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from app.controllers.user import check_admin, get_current_active_user
from app.models.models import PlaylistResponse
from app.services.spotify import SpotifyAPI
import os

router = APIRouter(
    prefix="/spotify",
    tags=["spotify"],
)


def check_environment():
    if os.environ.get("ENVIRONMENT", "dev") != "dev":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This method is not allowd in production",
        )


@router.get("/login", status_code=307, dependencies=[Depends(check_environment)])
def spotify_login() -> RedirectResponse:
    spotify = SpotifyAPI()
    return RedirectResponse(spotify.get_url_login())


@router.get("/callback", dependencies=[Depends(check_environment)])
def spotify_callback(code: str) -> dict:
    spotify = SpotifyAPI()
    token = spotify.get_token(code)
    return {"token": token}


@router.get(
    "/playlist", dependencies=[Depends(get_current_active_user), Depends(check_admin)]
)
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
