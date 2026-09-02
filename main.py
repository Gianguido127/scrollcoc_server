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
def update_links(payload: dict):
    path = Path("links.json")

    # --- 1. ESTRAZIONE SICURA DEI DATI ---
    # Accetta sia {"data": [...]} che direttamente [...]
    if isinstance(payload, list):
        new_data = payload
    elif isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], list):
        new_data = payload["data"]
    else:
        return JSONResponse(
            {"status": "error", "reason": "Payload must be a list or contain a 'data' list"},
            status_code=400
        )

    # --- 2. CARICAMENTO SICURO DEL FILE ---
    if path.exists():
        try:
            with open(path, "r") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
        except:
            existing = []
    else:
        existing = []

    # --- 3. UNIONE ---
    combined = existing + new_data

    # --- 4. RIMOZIONE DUPLICATI ---
    seen = set()
    unique = []
    for item in combined:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    # --- 5. SALVATAGGIO ---
    try:
        with open(path, "w") as f:
            json.dump(unique, f, indent=4)
    except Exception as e:
        return JSONResponse(
            {"status": "error", "reason": f"write_failed: {str(e)}"},
            status_code=500
        )

    return {"status": "ok", "added": len(new_data), "total": len(unique)}


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
