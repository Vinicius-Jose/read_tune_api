from fastapi import FastAPI
from dotenv import load_dotenv
from app.controllers.spotify import router as spotify_router
from app.controllers.llm import router as llm_router
from app.controllers.books import router as book_router


load_dotenv("./.env")
app = FastAPI()
app.include_router(spotify_router)
app.include_router(llm_router)
app.include_router(book_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
