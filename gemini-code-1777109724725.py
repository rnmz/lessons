import sqlite3
import random
import string
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, FileResponse

app = FastAPI()
letters = list(string.ascii_letters)

def init_db():
    conn = sqlite3.connect("links.db")
    conn.execute("CREATE TABLE IF NOT EXISTS links (short_id TEXT PRIMARY KEY, full_url TEXT)")
    conn.commit()
    conn.close()
init_db()

def get_db():
    conn = sqlite3.connect("links.db")
    # row_factory оставляем, чтобы обращаться к колонкам по именам, а не индексам
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/add")
def add_link(data: dict):
    # Добавляем подключение к базе данных
    conn = get_db()
    # Генерируем короткую ссылку (short_id)
    short_id = "".join(random.choice(letters) for _ in range(5))
    # Достаём полную ссылку из запроса пользователя
    full_url = data.get("full_url")

    # Тут код, что мы писали ранее
    try:
        # Пробуем добавить ссылку в базу данных
        conn.execute(
            "INSERT INTO links (short_id, full_url) VALUES (?, ?)",
            (short_id, full_url)
        )
        conn.commit()
        # возвращаем новую ссылку
        return {"short_id": short_id}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Already exists")
    finally:
        conn.close()

# 2. Перейти по ссылке
@app.get("/{short_id}")
def redirect_to_url(short_id):
    conn = get_db()
    row = conn.execute(
        "SELECT full_url FROM links WHERE short_id = ?", 
        (short_id,)
    ).fetchone()
    conn.close()
    
    if row:
        return RedirectResponse(url=row["full_url"])
    raise HTTPException(status_code=404)

# 3. Удалить ссылку
@app.delete("/delete/{short_id}")
def delete_link(short_id):
    conn = get_db()
    cursor = conn.execute("DELETE FROM links WHERE short_id = ?", (short_id,))
    conn.commit()
    conn.close()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404)
    return {"status": "deleted"}

