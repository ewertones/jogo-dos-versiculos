import os
import sqlite3

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

app = FastAPI(docs_url=None, redoc_url=None)

templates = Jinja2Templates(directory="templates")


DATABASE_PATH = os.path.join("bible", "ARC.sqlite")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("")
@app.get("/")
@app.get("/app")
async def index(request: Request) -> HTMLResponse:
    conn = get_db_connection()
    metadata = {}
    cur = conn.execute("SELECT key, value FROM metadata")
    for row in cur.fetchall():
        metadata[row["key"]] = row["value"]
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "metadata": metadata})


@app.get("/docs")
async def redirect_to_docs():
    """Homepage redirect to /app"""
    return RedirectResponse("/app", status_code=status.HTTP_301_MOVED_PERMANENTLY)


@app.get("/verse", response_class=JSONResponse)
async def get_random_verse():
    conn = get_db_connection()
    cur = conn.execute(
        """
  SELECT v.text,
         b.name AS book,
         v.chapter,
         v.verse
    FROM verse AS v
    JOIN book AS b
      ON v.book_id = b.id
   WHERE b.id >= 65
ORDER BY RANDOM()
   LIMIT 1
    """
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="No verse found")
    verse_data = {
        "text": row["text"],
        "book": row["book"],
        "chapter": row["chapter"],
        "verse": row["verse"],
    }
    return verse_data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
