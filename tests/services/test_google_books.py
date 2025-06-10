from dotenv import load_dotenv
from app.services.google_books import GoogleBooksAPI

load_dotenv("./.env")


def test_search_volume_by_title() -> None:
    api = GoogleBooksAPI()
    title = "The end of eternity"
    response = api.search_volume(title)
    items = response.get("items")
    assert len(items) > 0
    book_title: str = items[0].get("volumeInfo").get("title")
    assert title.lower() in book_title.lower()


def test_search_volume_by_author() -> None:
    api = GoogleBooksAPI()
    author = "Isaac Asimov"
    response = api.search_volume(author)
    items = response.get("items")
    assert len(items) > 0
    authors: str = items[0].get("volumeInfo").get("authors")
    assert author in authors


def test_search_volume_by_isbn() -> None:
    api = GoogleBooksAPI()
    isbn = "9780593160060"
    title = "The end of eternity"
    response = api.search_volume("isbn:" + isbn)
    items: list[dict] = response.get("items")
    assert len(items) > 0
    volume_info: dict = items[0].get("volumeInfo")
    book_title: str = volume_info.get("title")
    assert title.lower() in book_title.lower()
    isbn_response = volume_info["industryIdentifiers"][0].get("identifier")
    assert isbn_response == isbn


def test_get_volume() -> None:
    api = GoogleBooksAPI()
    volume_id = "HB-OEAAAQBAJ"
    title = "The End of Eternity"
    response = api.get_volume(volume_id)
    title_response: str = response["volumeInfo"]["title"]
    assert title.lower() == title_response.lower()
