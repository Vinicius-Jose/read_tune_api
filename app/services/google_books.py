import requests
import os


class GoogleBooksAPI:

    def __init__(self) -> None:
        self.key = os.environ.get("GOOGLE_API_KEY")
        self.url = "https://www.googleapis.com/books/v1/"

    def search_volume(self, search_query: str, max_results: int = 5) -> dict:
        url = f"{self.url}volumes/"
        params = {"q": search_query, "key": self.key, "maxResults": max_results}
        response = requests.get(url, params=params)
        return response.json()

    def get_volume(self, volume_id: str) -> dict:
        url = f"{self.url}volumes/{volume_id}"
        params = {"key": self.key}
        response = requests.get(url, params=params)
        return response.json()
