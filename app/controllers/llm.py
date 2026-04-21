import uuid
from app.models.models import Playlist, PlaylistResponse, Style
from app.models.states import OverallState
from app.services.google_books import GoogleBooksAPI
from app.services.llm_langgraph import LLMGraph

from fastapi import APIRouter, HTTPException, status

from app.services.streaming import StreamingAPI
from app.utils.prompts import styles
from app.controllers.streaming import Provider, StreamingAPIFactory

router = APIRouter(
    prefix="/llm",
    tags=["llm"],
)


@router.get("/style")
def get_style() -> list[Style]:
    response = []
    for key, value in styles.items():
        response.append(Style(name=key, description=value))
    return response


@router.get("/{volume_id}")
def get_playlist(
    volume_id: str,
    playlist_style: str = "Any Style",
    min_songs: int = 5,
    max_songs: int = 10,
    provider: Provider = Provider.youtube,
) -> PlaylistResponse:
    volume = get_volume_google_books(volume_id)
    volume["playlist_style"] = playlist_style
    volume["max_songs"] = max_songs
    volume["min_songs"] = min_songs
    streaming = StreamingAPIFactory().build(provider)
    query = f"{volume['book_title']} - {volume['book_authors']} - {volume['isbn']} - {volume['playlist_style']}"
    playlists = streaming.search(query, ["playlist"], limit=1)
    if len(playlists) > 0:
        playlist = playlists[0]
        if playlist.title.lower() == query.lower():
            playlist = streaming.get_playlist(playlist.content_id)
            return playlist

    graph = LLMGraph()
    thread_id = str(uuid.uuid4())
    playlist = graph.execute_graph(thread_id, volume)
    response = save_playlist(playlist["playlist"], streaming)
    return response


def get_volume_google_books(volume_id: str) -> OverallState:
    api = GoogleBooksAPI()
    volume = api.get_volume(volume_id)
    volume_info: dict = volume.get("volumeInfo")
    if not volume_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volume not found",
        )
    title: str = volume_info.get("title")
    authors: str = " ".join(volume_info.get("authors"))
    isbn_list: list[dict] = volume_info.get("industryIdentifiers")
    isbn = ""
    for item in isbn_list:
        if item.get("type") == "ISBN_13":
            isbn = item.get("identifier")
            break

    return OverallState(
        context=[volume.get("description")],
        book_title=title,
        book_authors=authors,
        isbn=isbn,
        category=" ".join(volume_info.get("categories")),
    )


def save_playlist(playlist: Playlist, api: StreamingAPI) -> PlaylistResponse:
    tracks_ids = []
    for song in playlist.song_list:
        query = f"{song.artist_name} {song.song_name}"
        tracks = api.search(query, limit=1)
        if len(tracks) > 0:
            track = tracks[0]
            if song.song_name.lower() in track.title.lower() and any(
                song.artist_name.lower() in author.lower() for author in track.authors
            ):
                tracks_ids.append(track.content_id)
    user_id = api.get_current_user()
    playlist_response = api.create_playlist(
        user_id, playlist.name, playlist.description
    )
    api.add_tracks_to_playlist(playlist_response.id, tracks_ids)

    return playlist_response
