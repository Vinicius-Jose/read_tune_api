from enum import Enum

from app.services.spotify import SpotifyAPI
from app.services.streaming import StreamingAPI
from app.services.youtube import YoutubeAPI


class Provider(str, Enum):
    spotify = "spotify"
    youtube = "youtube"


class StreamingAPIFactory:
    def __init__(self) -> None:
        self.__apis = {
            "spotify": SpotifyAPI,
            "youtube": YoutubeAPI,
        }

    def build(self, provider: Provider) -> StreamingAPI:
        return self.__apis.get(provider.name)()
