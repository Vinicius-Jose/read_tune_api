from fastapi import APIRouter

from app.models.models import BookResponse

router = APIRouter(prefix="books/")


@router.get("/")
def search(query: str = None) -> BookResponse:
    "TODO"
    pass
