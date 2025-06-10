from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from app.models.models import Playlist
from app.models.states import OverallState, OutputState
from app.services.google_books import GoogleBooksAPI
from app.utils.prompts import llm_instructions, styles
import os
from app.utils.tools import singleton


@singleton
class LLMGraph:

    def __init__(self, graph_image_path: str = "") -> None:
        self.llm = ChatGroq(model=os.environ.get("GROQ_MODEL"))
        self.structured_llm = self.llm.with_structured_output(Playlist)
        self.graph = self.__build_graph(graph_image_path)

    def search_wikipedia(self, state: OverallState) -> OverallState:
        query = f"{state['book_title']} {state['book_authors']}"
        search_docs = WikipediaLoader(query=query, load_max_docs=1).load()

        formatted_search_docs = "\n\n---\n\n".join(
            [f'<Document">\n{doc.page_content}\n</Document>' for doc in search_docs]
        )

        return {"context": [formatted_search_docs]}

    def search_tavily(self, state: OverallState) -> OverallState:
        tavily_search = TavilySearchResults(max_results=3)
        query = f"{state['book_title']} {state['book_authors']} ISBN: {state['isbn']}"
        query = f"Summary for the book {query}"
        search_docs = tavily_search.invoke(query)

        formatted_search_docs = "\n\n---\n\n".join(
            [f'<Document >\n{doc["content"]}\n</Document>' for doc in search_docs]
        )

        return {"context": [formatted_search_docs]}

    def llm_generate_playlist(self, state: OverallState) -> OutputState:
        book_info = (
            f"{state['book_title']} {state['book_authors']} ISBN: {state['isbn']}"
        )

        playlist_style = state["playlist_style"]
        style_description = styles.get(playlist_style, styles.get("Any Style"))
        query_style = f"Style:{playlist_style} - Style Description {style_description}"
        instructions = llm_instructions.format(
            max_songs=state["max_songs"],
            min_songs=state["min_songs"],
            book_info=book_info,
            context=state["context"],
            style=query_style,
            category=state["category"],
        )
        playlist = self.structured_llm.invoke(
            [SystemMessage(content=instructions)]
            + [HumanMessage(content="Generate the playlist")]
        )
        return {"playlist": playlist}

    def __build_graph(self, graph_image_path: str = None) -> CompiledStateGraph:
        graph = StateGraph(OverallState, output=OutputState)

        graph.add_node("search_wikipedia", self.search_wikipedia)
        graph.add_node("search_tavily", self.search_tavily)
        graph.add_node("llm_generate_playlist", self.llm_generate_playlist)

        graph.add_edge(START, "search_wikipedia")
        graph.add_edge(START, "search_tavily")
        graph.add_edge("search_wikipedia", "llm_generate_playlist")
        graph.add_edge("search_tavily", "llm_generate_playlist")
        graph.add_edge("llm_generate_playlist", END)

        graph = graph.compile()
        if graph_image_path:
            with open(graph_image_path, "wb") as image:
                img_graph = graph.get_graph().draw_mermaid_png()
                image.write(img_graph)
        return graph

    def execute_graph(self, thread_id: str, state: OverallState) -> OutputState:
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(state, config)
