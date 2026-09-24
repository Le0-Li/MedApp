"""FastAPI application entrypoint.

Creates the app, configures CORS, and mounts the routers that hold the
actual endpoint logic (see app/routers/).
"""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers import api_router

app = FastAPI(title="Backend Technical Exercise")

# Allow the local Vite dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Each router owns one resource's endpoints - see app/routers/slots.py and
# app/routers/bookings.py for the actual route definitions.
app.include_router(api_router)


@app.get("/")
def read_root() -> dict[str, str]:
    """Basic liveness message for the API root."""
    return {"message": "Backend starter is running"}


@app.get("/health")
def healthcheck(db: Session = Depends(get_db)) -> dict[str, str]:
    """Confirm the API process can reach the database."""
    db.execute(text("SELECT 1"))
    return {"status": "ok"}