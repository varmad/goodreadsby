"""FastAPI service (ADR-0004): owns the API the public site reads from.

For the walking skeleton it exposes a single read: a Work and all of its
Recommendations, already shaped for public consumption by the presenter.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .db.repository import get_work_by_slug
from .db.session import get_session
from .domain.presenter import present_work

app = FastAPI(title="goodreadsby API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/works/{slug}")
def read_work(slug: str, session: Session = Depends(get_session)) -> dict:
    result = get_work_by_slug(session, slug)
    if result is None:
        raise HTTPException(status_code=404, detail="Work not found")
    work, recommendations, editions = result
    return present_work(work, recommendations, editions)
