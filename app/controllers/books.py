from fastapi import APIRouter

from app.models.models import BookResponse
from app.services.google_books import GoogleBooksAPI

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/")
def search(query: str, max_results: int = 5) -> list[BookResponse]:
    books_api = GoogleBooksAPI()
    volumes = books_api.search_volume(query, max_results)
    response = []
    for item in volumes["items"]:
        isbn = ""
        volume_info: dict = item.get("volumeInfo")
        for isbn_item in volume_info.get("industryIdentifiers", []):
            if isbn_item.get("type") == "ISBN_13":
                isbn = isbn_item.get("identifier")
                break
        volume = BookResponse(
            volume_id=item.get("id"),
            title=volume_info.get("title"),
            authors=volume_info.get("authors", []),
            description=volume_info.get("description", ""),
            isbn=isbn,
            categories=volume_info.get("categories", []),
            thumbnail=volume_info.get("imageLinks", {}).get("thumbnail"),
            language=volume_info.get("language"),
        )
        response.append(volume)

    return response
