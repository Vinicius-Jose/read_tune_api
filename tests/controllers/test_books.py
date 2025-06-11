from fastapi.testclient import TestClient
from app.main import app
from tests.test_main import authenticate
import pytest
import os

client = TestClient(app)


@pytest.mark.parametrize(
    "query,max_results",
    [("The end of eternity", 5), ("Starters", 3), ("Humans like gods H.G. Wells", 3)],
)
def test_books_search(query: str, max_results: int) -> None:
    headers = authenticate(os.environ["EMAIL_CLIENT"], os.environ["PWD_CLIENT"])
    params = {"query": query, "max_results": max_results}
    response = client.get("books/", params=params, headers=headers)
    assert response.status_code == 200
    response = response.json()
    assert len(response) <= max_results
    assert response[0].get("title")


def test_books_search_unauthorized() -> None:
    params = {"query": "Test", "max_results": 5}
    response = client.get("books/", params=params)
    assert response.status_code == 401
