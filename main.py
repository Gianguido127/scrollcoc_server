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
    # Accetta:
    # - lista pura
    # - dict con "data"
    # - dict con "chunk"
    # - qualsiasi cosa che contenga una lista
    new_data = None

    if isinstance(payload, list):
        new_data = payload

    elif isinstance(payload, dict):
        # Cerca una lista in qualsiasi chiave
        for key, value in payload.items():
            if isinstance(value, list):
                new_data = value
                break

    # Se non abbiamo trovato una lista → errore controllato
    if not isinstance(new_data, list):
        return JSONResponse(
            {"status": "error", "reason": "Payload must contain a list"},
            status_code=400
        )

    # --- 2. CARICAMENTO SICURO DEL FILE ---
    existing = []
    if path.exists():
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    existing = data
        except Exception:
            existing = []

    # --- 3. UNIONE DEI CHUNK (senza assumere tipi hashabili) ---
    combined = existing + new_data

    # --- 4. RIMOZIONE DUPLICATI SENZA set() ---
    unique = []
    for item in combined:
        # Confronto sicuro: JSON string
        try:
            marker = json.dumps(item, sort_keys=True)
        except Exception:
            # Se non serializzabile → lo salviamo comunque
            marker = str(item)

        if marker not in unique:
            unique.append(marker)

    # Convertiamo i marker JSON in oggetti veri
    final_data = []
    for marker in unique:
        try:
            final_data.append(json.loads(marker))
        except Exception:
            final_data.append(marker)

    # --- 5. SCRITTURA SICURA ---
    try:
        with open(path, "w") as f:
            json.dump(final_data, f, indent=4)
    except Exception as e:
        return JSONResponse(
            {"status": "error", "reason": f"write_failed: {str(e)}"},
            status_code=500
        )

    return {
        "status": "ok",
        "added": len(new_data),
        "total": len(final_data)
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
