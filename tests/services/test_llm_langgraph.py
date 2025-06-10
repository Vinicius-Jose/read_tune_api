import uuid
from dotenv import load_dotenv
from app.services.llm_langgraph import LLMGraph
from app.models.states import OverallState

load_dotenv("./.env")


def test_search_wikipedia() -> None:
    state = OverallState(book_title="The End of Eternity", book_authors="Isaac Asimov")
    graph = LLMGraph()
    wikipedia_docs = graph.search_wikipedia(state).get("context")
    assert wikipedia_docs[0]


def test_search_wikipedia_book_not_exists() -> None:
    state = OverallState(book_title="Naruto vs Dragon Ball", book_authors="Neymar")
    graph = LLMGraph()
    wikipedia_docs = graph.search_wikipedia(state).get("context")
    assert wikipedia_docs[0] == ""


def test_search_tavily() -> None:
    state = OverallState(
        book_title="The End of Eternity",
        book_authors="Isaac Asimov",
        isbn="9780593160022",
    )
    graph = LLMGraph()
    tavily_docs = graph.search_tavily(state).get("context")
    assert tavily_docs[0]


def test_llm_generate_playlist() -> None:
    state = OverallState(
        book_title="The End of Eternity",
        book_authors="Isaac Asimov",
        isbn="9780593160022",
        max_songs=10,
        min_songs=5,
        playlist_style="Classical",
        context="A spellbinding novel set in the universe of Isaac Asimov’s classic Galactic Empire series and Foundation series\u003cbr\u003e\u003c/b\u003e\u003cbr\u003e\u003ci\u003eDue to circumstances within our control . . . tomorrow will be canceled.\u003c/i\u003e\u003cbr\u003e\u003cbr\u003eThe Eternals, the ruling class of the Future, had the power of life and death not only over every human being but over the very centuries into which they were born. Past, Present, and Future could be created or destroyed at will.\u003cbr\u003e\u003cbr\u003e You had to be special to become an Eternal. Andrew Harlan was special. Until he committed the one unforgivable sin—falling in love.\u003cbr\u003e\u003cbr\u003e Eternals weren’t supposed to have feelings. But Andrew could not deny the sensations that were struggling within him. He knew he could not keep this secret forever. And so he began to plan his escape, a plan that changed his own past . . . and threatened Eternity itself.",
        category="Sci-Fi",
    )
    graph = LLMGraph()
    result = graph.llm_generate_playlist(state)
    playlist = result["playlist"]
    assert len(playlist.song_list) > 0
    assert playlist.description
    assert playlist.name


def test_build_graph() -> None:
    llm_graph = LLMGraph()
    graph = llm_graph.graph
    assert len(graph.nodes) > 0


def test_build_graph_save_image() -> None:
    llm_graph = LLMGraph(graph_image_path="./graph.jpg")
    graph = llm_graph.graph
    assert len(graph.nodes) > 0


def test_singleton() -> None:
    instance_1 = LLMGraph()
    instance_2 = LLMGraph()
    assert instance_1.graph == instance_2.graph


def test_execute_graph() -> None:
    state = OverallState(
        book_title="The End of Eternity",
        book_authors="Isaac Asimov",
        isbn="9780593160022",
        max_songs=10,
        min_songs=5,
        playlist_style="Classical",
        category="Sci-Fi",
    )
    llm_graph = LLMGraph(graph_image_path="./graph.jpg")
    playlist = llm_graph.execute_graph(uuid.uuid4(), state)
    assert len(playlist["playlist"].song_list) > 0
