from fastapi import Cookie, Response

from app.session import generate_session_id


def get_session_id(
    response: Response,
    session_id: str | None = Cookie(default=None),
) -> str:
    if session_id is None:
        session_id = generate_session_id()

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="lax",
            secure=False,  # True en production avec HTTPS
            max_age=60 * 60 * 24 * 30,
        )

    return session_id