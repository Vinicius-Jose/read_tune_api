from fastapi import APIRouter, Depends

from app.controllers.user import check_admin, get_current_active_user
from app.models.models import PlaylistResponse
from app.services.youtube import YoutubeAPI


router = APIRouter(
    prefix="/youtube",
    tags=["youtube"],
)


@router.get(
    "/playlist", dependencies=[Depends(get_current_active_user), Depends(check_admin)]
)
def youtube_playlist() -> list[PlaylistResponse]:
    youtube = YoutubeAPI()
    user_id = youtube.get_current_user()
    response = youtube.get_playlists_user(user_id)
    return response
