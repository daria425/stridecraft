from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from stridecraft.api.state import AppState
from stridecraft.content.registry import Content
from stridecraft.db.repositories import UserRepository
from stridecraft.errors import NotLoggedInError
from stridecraft.models import User


def get_state(request: Request) -> AppState:
    return request.app.state.stridecraft


def get_session(state: Annotated[AppState, Depends(get_state)]) -> Iterator[Session]:
    with state.database.session() as session:
        yield session


def get_content(state: Annotated[AppState, Depends(get_state)]) -> Content:
    return state.content


def current_user(request: Request, session: Annotated[Session, Depends(get_session)]) -> User:
    """The logged-in user, from the signed session cookie. Every `/me` route depends on this and
    nothing else identifies a user, so one user can never reach another's data."""
    user_id = request.session.get("user_id")
    user = user_id and UserRepository(session).get(user_id)
    if not user:
        request.session.clear()
        raise NotLoggedInError("Log in with Strava first")
    return user


State = Annotated[AppState, Depends(get_state)]
DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(current_user)]
GameContent = Annotated[Content, Depends(get_content)]
