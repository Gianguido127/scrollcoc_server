from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import json
from pathlib import Path
from pydantic import BaseModel

app = FastAPI()

# Homepage → restituisce index.html
@app.get("/")
def home():
    return FileResponse("index.html")

# API → restituisce il contenuto di links.json (nella root)
@app.get("/api/links")
def get_links():
    path = Path("links.json")
    if not path.exists():
        return JSONResponse([], status_code=200)

    with open(path, "r") as f:
        data = json.load(f)

    return JSONResponse(data)

class LinksPayload(BaseModel):
    data: list

@app.put("/update_links")
def update_links(payload: LinksPayload):
    path = Path("links.json")

    # 1. Se il file esiste, carica i dati attuali
    if path.exists():
        with open(path, "r") as f:
            existing = json.load(f)
    else:
        existing = []

    # 2. Aggiungi i nuovi ID al database
    combined = existing + payload.data

    # 3. Rimuovi duplicati mantenendo l'ordine
    seen = set()
    unique = []
    for item in combined:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    # 4. Salva il risultato completo
    with open(path, "w") as f:
        json.dump(unique, f, indent=4)

    return {"status": "ok", "added": len(payload.data), "total": len(unique)}


@app.get("/count")
def count_links():
    path = Path("links.json")
    if not path.exists():
        return {"count": 0}

    with open(path, "r") as f:
        data = json.load(f)

    return {"count": len(data)}

@app.get("/ping")
def ping():
    return {"status": "ok"}
