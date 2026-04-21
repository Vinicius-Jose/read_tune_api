import os
from app.models.models import PlaylistResponse, SearchItem
from app.services.streaming import StreamingAPI
from google.oauth2.credentials import Credentials

from google_auth_oauthlib.flow import Flow

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import time


class YoutubeAPI(StreamingAPI):

    def __init__(self) -> None:
        self.client_secret_file = os.environ.get("GOOGLE_JSON")
        self.flow = Flow.from_client_secrets_file(
            self.client_secret_file,
            scopes=[
                "https://www.googleapis.com/auth/youtube",
            ],
        )
        self.flow.redirect_uri = "http://localhost:8000/callback"
        self.__youtube = None
        self.__credentials = None

    def get_url_login(self) -> str:

        authorization_url, _ = self.flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )
        return authorization_url

    def get_refresh_token(self, code: str = "") -> Credentials:
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials
        return credentials

    def __authenticate(self) -> None:
        if not self.__credentials:
            self.__credentials = Credentials.from_authorized_user_file(
                os.environ.get("GOOGLE_TOKEN_JSON_FILE")
            )
            self.__youtube: Resource = build(
                "youtube", "v3", credentials=self.__credentials
            )

    def search(
        self, query: str, search_type: list[str] = ["video"], limit=5
    ) -> list[SearchItem]:
        self.__authenticate()
        params = {
            "part": "snippet,id",
            "q": query,
            "type": search_type[0],
            "maxResults": limit,
        }
        if search_type[0] == "video":
            params["videoCategoryId"] = 10
        request = self.__youtube.search().list(**params)
        data = request.execute()
        return self.__normalize_search_result(data, search_type[0])

    def get_current_user(self) -> str:
        self.__authenticate()
        request = self.__youtube.channels().list(part="snippet,id", mine=True)
        data = request.execute()
        return data["items"][0]["id"]

    def create_playlist(
        self, user_id: str, name: str, description: str, public: bool = True
    ) -> PlaylistResponse:
        self.__authenticate()
        request = self.__youtube.playlists().insert(
            part="snippet,status,player",
            body={
                "snippet": {
                    "title": name,
                    "description": description,
                    "defaultLanguage": "en",
                },
                "status": {"privacyStatus": "public" if public else "private"},
            },
        )
        data = request.execute()
        return PlaylistResponse(
            id=data["id"], link=data["player"]["embedHtml"], title=name
        )

    def add_tracks_to_playlist(
        self, playlist_id: str, tracks_uris: str | list[str]
    ) -> dict:
        self.__authenticate()
        if isinstance(tracks_uris, str):
            tracks_uris = [tracks_uris]
        for track in tracks_uris:
            try:
                request = self.__youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {"kind": "youtube#video", "videoId": track},
                        }
                    },
                )
                request.execute()
            except HttpError as error:
                time.sleep(1)
                print(error)

        return {"Playlist": playlist_id}

    def unfollow_playlist(self, playlist_id: str) -> None:
        self.__authenticate()
        request = self.__youtube.playlists().delete(id=playlist_id)
        return request.execute()

    def get_playlist(self, playlist_id: str) -> PlaylistResponse:
        self.__authenticate()
        request = self.__youtube.playlists().list(
            part="snippet,id,player", id=playlist_id, maxResults=1
        )
        data = request.execute()[0]
        return PlaylistResponse(id=data["id"], link=data["player"]["embedHtml"])

    def get_playlists_user(
        self, user_id: str, limit: int = 10
    ) -> list[PlaylistResponse]:
        self.__authenticate()
        request = self.__youtube.playlists().list(
            part="snippet,id,player", channelId=user_id, maxResults=limit
        )
        data = request.execute()
        playlists = []
        for item in data.get("items"):
            playlist = PlaylistResponse(
                id=item.get("id"),
                link=item.get("player", {}).get("embedHtml", ""),
                title=item.get("snippet").get("title"),
            )
            playlists.append(playlist)
        return playlists

    def __normalize_search_result(
        self, data: dict, search_type: str
    ) -> list[SearchItem]:
        items = []
        for item in data.get("items"):
            search_item = SearchItem(
                content_id=item.get("id").get(f"{search_type}Id"),
                content_type=search_type,
                authors=[item.get("snippet").get("channelTitle")],
                title=item.get("snippet").get("title"),
            )
            items.append(search_item)
        return items
