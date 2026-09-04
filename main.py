from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import json
from pathlib import Path
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

ADMINS = {
    "superadmin": "Juve1897$",
}


app = FastAPI()

# Homepage → restituisce index.html
@app.get("/")
def home():
    return FileResponse("index.html")

# API → restituisce il contenuto di links.json (nella root)
@app.get("/api/links")
def get_links(request: Request):
    user_agent = request.headers.get("User-Agent", "").lower()

    # Se è un browser → pagina vuota
    if "mozilla" in user_agent or "chrome" in user_agent or "safari" in user_agent or "firefox" in user_agent:
        return HTMLResponse("")  # pagina bianca

    # Altrimenti → restituisci il JSON per gli script
    path = Path("links.json")
    if not path.exists():
        return JSONResponse([], status_code=200)

    with open(path, "r") as f:
        data = json.load(f)

    return JSONResponse(data)


from fastapi import Request

@app.put("/update_links")
async def update_links(request: Request):
    path = Path("links.json")

    # --- 1. LEGGI IL JSON GREZZO SENZA VALIDAZIONE FASTAPI ---
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            {"status": "error", "reason": "Invalid JSON"},
            status_code=400
        )

    # --- 2. ESTRAI LA LISTA DEI CHUNK ---
    if not isinstance(payload, dict):
        return JSONResponse(
            {"status": "error", "reason": "Payload must be a dict"},
            status_code=400
        )

    if "data" not in payload or not isinstance(payload["data"], list):
        return JSONResponse(
            {"status": "error", "reason": "'data' must be a list"},
            status_code=400
        )

    new_data = payload["data"]

    # --- 3. CARICA IL FILE ESISTENTE ---
    existing = []
    if path.exists():
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    existing = data
        except Exception:
            existing = []

    # --- 4. UNISCI I CHUNK ---
    combined = existing + new_data

    # --- 5. RIMOZIONE DUPLICATI (FUNZIONA CON DIZIONARI) ---
    seen = set()
    unique = []
    for item in combined:
        marker = json.dumps(item, sort_keys=True)
        if marker not in seen:
            seen.add(marker)
            unique.append(item)

    # --- 6. SALVA ---
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
        "added": len(new_data),
        "total": len(unique)
    }

@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/t1m2s7", response_class=HTMLResponse)
def admin_page(request: Request):
    user = request.cookies.get("admin_user")

    # se non loggato → redirect
    if user not in SESSIONS:
        return RedirectResponse("/login_admin")

    html_path = Path("admin.html")
    return html_path.read_text(encoding="utf-8")


from auto_update_shorts_server import run_update
@app.post("/t1m2s7/update_database")
def update_database(request: Request):
    user = request.cookies.get("admin_user")
    if user not in SESSIONS:
        return RedirectResponse("/login_admin")

    result = run_update()
    return result


from fastapi import Request

@app.get("/login_admin", response_class=HTMLResponse)
def login_admin_page():
    return Path("login_admin.html").read_text(encoding="utf-8")

from fastapi.responses import RedirectResponse

SESSIONS = set()  # contiene gli username loggati

@app.post("/login_admin")
async def login_admin(request: Request):
    data = await request.json()

    username = data.get("username")
    password = data.get("password")

    if username in ADMINS and ADMINS[username] == password:
        # salva la sessione
        SESSIONS.add(username)

        # crea la risposta
        response = JSONResponse({"status": "ok"})
        response.set_cookie("admin_user", username, max_age=3600)  # 1 ora
        return response

    return {"status": "error", "reason": "Credenziali non valide"}
