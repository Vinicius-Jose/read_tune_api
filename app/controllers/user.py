from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from datetime import datetime, timedelta, timezone
import os
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from app.models.models import Token, TokenData, User

from fastapi.concurrency import asynccontextmanager

from sqlmodel import SQLModel, Session, create_engine

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

sqlite_url = os.environ["SQL_URL"]
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

router = APIRouter()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: SessionDep, email: str):
    user: Union[None, User] = db.get(User, email)
    return user


def authenticate_user(session: SessionDep, email: str, password: str):
    user = get_user(session, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def check_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't access this method",
        )


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="Bearer")


@router.get("/users/me/", response_model=User, tags=["user"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.post(
    "/user/",
    dependencies=[
        Depends(get_current_active_user),
        Depends(check_admin),
    ],
    tags=["user"],
)
def create_user(user: User, session: SessionDep) -> User:
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
