import os
import sqlite3
import random

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

app = FastAPI(docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")

DATABASE_PATH = os.path.join("bible", "ARC.sqlite")

# Global cache to store verses in memory
verses_cache = []


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def load_verses():
    """Load all verses into memory at startup."""
    global verses_cache
    conn = get_db_connection()
    cur = conn.execute(
        """
        SELECT v.text,
               b.name AS book,
               v.chapter,
               v.verse
          FROM verse AS v
          JOIN book AS b ON v.book_id = b.id
         WHERE b.id >= 65
         ORDER BY RANDOM()
         """
    )
    # Convert rows to dictionaries for easier handling
    verses_cache = [dict(row) for row in cur.fetchall()]
    conn.close()


@app.get("")
@app.get("/")
@app.get("/app")
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/docs")
async def redirect_to_docs():
    """Homepage redirect to /app"""
    return RedirectResponse("/app", status_code=status.HTTP_301_MOVED_PERMANENTLY)


@app.get("/verse", response_class=JSONResponse)
async def get_random_verse():
    if not verses_cache:
        raise HTTPException(status_code=404, detail="Nenhum versículo encontrado.")
    verse = random.choice(verses_cache)
    return verse


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
