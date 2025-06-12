import uuid
from app.models.models import Playlist, PlaylistResponse, Style
from app.models.states import OverallState
from app.services.google_books import GoogleBooksAPI
from app.services.llm_langgraph import LLMGraph
from app.services.spotify import SpotifyAPI
from fastapi import APIRouter
from app.utils.prompts import styles

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
) -> PlaylistResponse:
    volume = get_volume_google_books(volume_id)
    volume["playlist_style"] = playlist_style
    volume["max_songs"] = max_songs
    volume["min_songs"] = min_songs
    spotify = SpotifyAPI()
    query = f"{volume['book_title']} - {volume['book_authors']} - {volume['isbn']} - {volume['playlist_style']}"
    search = spotify.search(query, ["playlist"])
    playlists = search["playlists"]["items"]

    if len(playlists) > 0:
        playlist = playlists[0]
        if playlist["name"].lower() == query.lower():
            response = PlaylistResponse(
                link=playlist["external_urls"]["spotify"], id=playlist["id"]
            )
            return response

    graph = LLMGraph()
    thread_id = str(uuid.uuid4())
    playlist = graph.execute_graph(thread_id, volume)
    response = save_playlist(playlist["playlist"], spotify)
    return response


def get_volume_google_books(volume_id: str) -> OverallState:
    api = GoogleBooksAPI()
    volume = api.get_volume(volume_id)
    volume_info: dict = volume.get("volumeInfo")
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


def save_playlist(playlist: Playlist, api: SpotifyAPI) -> PlaylistResponse:
    uris = []
    for song in playlist.song_list:
        query = f"{song.artist_name} {song.song_name}"
        search_response = api.search(query)
        tracks = search_response["tracks"]["items"]
        if len(tracks) > 0:
            track = tracks[0]
            artists = [artist.get("name").lower() for artist in track["artists"]]
            if (
                song.song_name.lower() in track["name"].lower()
                and song.artist_name.lower() in artists
            ):
                uris.append(track["uri"])
    user_id = api.get_current_user()["id"]
    playlist_spotify = api.create_playlist(user_id, playlist.name, playlist.description)
    api.add_tracks_to_playlist(playlist_spotify["id"], uris)
    playlist_response = PlaylistResponse(
        id=playlist_spotify["id"], link=playlist_spotify["external_urls"]["spotify"]
    )
    return playlist_response
