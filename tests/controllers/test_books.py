from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


@pytest.mark.parametrize(
    "query,max_results",
    [("The end of eternity", 5), ("Starters", 3), ("Humans like gods H.G. Wells", 3)],
)
def test_books_search(query: str, max_results: int) -> None:
    params = {"query": query, "max_results": max_results}
    response = client.get("books/", params=params)
    assert response.status_code == 200
    response = response.json()
    assert len(response) <= max_results
    assert response[0].get("title")
