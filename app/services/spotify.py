import requests
import os
import base64


class SpotifyAPI:
    def __init__(self) -> None:
        self.url: str = "https://api.spotify.com/v1/"
        self.__headers: dict = {}
        self.client_id: str = os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_secret: str = os.environ.get("SPOTIFY_CLIENT_SECRET")
        self.refresh_token: str = os.environ.get("SPOTIFY_REFRESH_TOKEN")

    def get_url_login(self) -> str:
        redirect_uri = os.environ.get("REDIRECT_URI")
        scope_list = [
            "playlist-modify-private",
            "playlist-modify-public",
            "user-read-private",
            "user-read-email",
            "playlist-read-private",
            "playlist-read-collaborative",
        ]
        scope_str = "%20".join(scope_list)
        return f"https://accounts.spotify.com/authorize?client_id={self.client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope_str}"

    def get_token(self, code: str = "") -> dict:
        if self.__headers.get("Authorization"):
            return self.__headers
        url: str = "https://accounts.spotify.com/api/token"
        auth = f"{self.client_id}:{self.client_secret}".encode()
        auth = base64.b64encode(auth).decode("utf-8")
        headers: dict = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth}",
        }

        payload = f"grant_type=authorization_code&code={code}&redirect_uri={os.environ.get('REDIRECT_URI')}"
        if not code:
            payload = f"grant_type=refresh_token&refresh_token={self.refresh_token}"

        response = requests.post(url, headers=headers, data=payload)
        response_json = response.json()
        self.__headers.update(
            {
                "Authorization": f"{response_json['token_type']} {response_json['access_token']}"
            }
        )
        os.environ["SPOTIFY_REFRESH_TOKEN"] = response_json.get(
            "refresh_token", self.refresh_token
        )
        self.refresh_token = response_json.get("refresh_token", self.refresh_token)
        return response_json

    def search(self, query: str, search_type: list[str] = ["track"], limit=5) -> dict:
        self.get_token()
        url = f"{self.url}search"
        params = {"q": query, "type": search_type, "limit": limit}
        response = requests.get(url, headers=self.__headers, params=params)
        return response.json()

    def get_current_user(self) -> dict:
        self.get_token()
        url = f"{self.url}me"
        response = requests.get(url, headers=self.__headers)
        return response.json()

    def create_playlist(
        self, user_id: str, name: str, description: str, public: bool = False
    ) -> dict:
        self.get_token()
        url = f"{self.url}users/{user_id}/playlists"
        payload = {
            "name": name,
            "description": description,
            "public": public,
        }
        response = requests.post(url, headers=self.__headers, json=payload)
        return response.json()

    def add_tracks_to_playlist(self, playlist_id: str, tracks_uris: list[str]) -> dict:
        self.get_token()
        url = f"{self.url}playlists/{playlist_id}/tracks"
        payload = {
            "uris": tracks_uris,
        }
        response = requests.post(url, headers=self.__headers, json=payload)
        return response.json()

    def unfollow_playlist(self, playlist_id: str) -> None:
        self.get_token()
        url = f"{self.url}playlists/{playlist_id}/followers"
        requests.delete(url, headers=self.__headers)

    def get_playlist(self, playlist_id: str) -> dict:
        self.get_token()
        url = f"{self.url}playlists/{playlist_id}"
        response = requests.get(url, headers=self.__headers)
        return response.json()

    def get_playlists_user(self, user_id: str, limit: int = 10) -> dict:
        self.get_token()
        url = f"{self.url}users/{user_id}/playlists"
        params = {"limit": limit}
        response = requests.get(url, headers=self.__headers, params=params)
        return response.json()
