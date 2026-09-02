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

    # --- 1. VALIDAZIONE DEL PAYLOAD ---
    # Se payload.data NON è una lista → errore controllato (non crash)
    if not isinstance(payload.data, list):
        return JSONResponse(
            {"status": "error", "reason": "payload.data must be a list"},
            status_code=400
        )

    # --- 2. CARICAMENTO SICURO DEL FILE ESISTENTE ---
    if path.exists():
        try:
            with open(path, "r") as f:
                existing = json.load(f)

            # Se il file NON contiene una lista → reset
            if not isinstance(existing, list):
                existing = []

        except Exception:
            # Se il file è corrotto → reset
            existing = []
    else:
        existing = []

    # --- 3. UNIONE DEI CHUNK ---
    combined = existing + payload.data

    # --- 4. RIMOZIONE DUPLICATI MANTENENDO L'ORDINE ---
    seen = set()
    unique = []
    for item in combined:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    # --- 5. SALVATAGGIO SICURO ---
    try:
        with open(path, "w") as f:
            json.dump(unique, f, indent=4)
    except Exception as e:
        return JSONResponse(
            {"status": "error", "reason": f"write_failed: {str(e)}"},
            status_code=500
        )

    return {
        "status": "ok",
        "added": len(payload.data),
        "total": len(unique)
    }


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
