from fastapi import Depends, FastAPI
from dotenv import load_dotenv


from app.controllers.spotify import router as spotify_router
from app.controllers.llm import router as llm_router
from app.controllers.books import router as book_router
from app.controllers.user import (
    check_admin,
    get_current_active_user,
    lifespan,
    router as user_router,
)


load_dotenv("./.env")


app = FastAPI(lifespan=lifespan)
app.include_router(
    spotify_router,
    dependencies=[Depends(get_current_active_user), Depends(check_admin)],
)
app.include_router(llm_router, dependencies=[Depends(get_current_active_user)])
app.include_router(book_router, dependencies=[Depends(get_current_active_user)])
app.include_router(user_router)
