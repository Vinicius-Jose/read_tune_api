from abc import abstractmethod, ABC

from app.models.models import PlaylistResponse, SearchItem


class StreamingAPI(ABC):

    @abstractmethod
    def search(
        self, query: str, search_type: list[str] = ["track"], limit=5
    ) -> list[SearchItem]:
        pass

    @abstractmethod
    def get_current_user(self) -> str:
        pass

    @abstractmethod
    def create_playlist(
        self, user_id: str, name: str, description: str, public: bool = False
    ) -> PlaylistResponse:
        pass

    @abstractmethod
    def add_tracks_to_playlist(
        self, playlist_id: str, tracks_uris: list[str] | str
    ) -> dict:
        pass

    @abstractmethod
    def unfollow_playlist(self, playlist_id: str) -> None:
        pass

    @abstractmethod
    def get_playlist(self, playlist_id: str) -> PlaylistResponse:
        pass

    @abstractmethod
    def get_playlists_user(
        self, user_id: str, limit: int = 10
    ) -> list[PlaylistResponse]:
        pass
