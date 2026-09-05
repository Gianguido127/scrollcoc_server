from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, RedirectResponse
import json
from pathlib import Path

app = FastAPI()

# ---------------------------
# CONFIGURAZIONE ADMIN
# ---------------------------

ADMINS = {
    "superadmin": "Juve1897$",
}

SESSIONS = set()  # utenti loggati

# ---------------------------
# HOMEPAGE
# ---------------------------

@app.get("/")
def home():
    return FileResponse("index.html")

# ---------------------------
# API LINKS
# ---------------------------

@app.get("/api/links")
def get_links():
    path = Path("links.json")
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)

# ---------------------------
# UPDATE LINKS
# ---------------------------

@app.put("/update_links")
async def update_links(request: Request):
    path = Path("links.json")
    payload = await request.json()

    if "data" not in payload or not isinstance(payload["data"], list):
        return JSONResponse({"status": "error", "reason": "'data' must be a list"}, status_code=400)

    new_data = payload["data"]

    existing = []
    if path.exists():
        try:
            with open(path, "r") as f:
                existing = json.load(f)
        except:
            existing = []

    combined = existing + new_data

    seen = set()
    unique = []
    for item in combined:
        marker = json.dumps(item, sort_keys=True)
        if marker not in seen:
            seen.add(marker)
            unique.append(item)

    with open(path, "w") as f:
        json.dump(unique, f, indent=4)

    return {"status": "ok", "added": len(new_data), "total": len(unique)}

# ---------------------------
# PING
# ---------------------------

@app.get("/ping")
def ping():
    return {"status": "ok"}

# ---------------------------
# PAGINA ADMIN (protetta)
# ---------------------------

@app.get("/t1m2s7", response_class=HTMLResponse)
def admin_page(request: Request):
    user = request.cookies.get("admin_user")
    if user not in SESSIONS:
        return RedirectResponse("/login_admin")
    return Path("admin.html").read_text(encoding="utf-8")

# ---------------------------
# UPDATE DATABASE (protetto)
# ---------------------------

from auto_update_shorts_server import run_update

@app.post("/t1m2s7/update_database")
def update_database(request: Request):
    user = request.cookies.get("admin_user")
    if user not in SESSIONS:
        return RedirectResponse("/login_admin")
    return run_update()

# ---------------------------
# PAGINA LOGIN
# ---------------------------

@app.get("/login_admin", response_class=HTMLResponse)
def login_admin_page():
    return Path("login_admin.html").read_text(encoding="utf-8")

# ---------------------------
# LOGIN ADMIN SEMPLICE
# ---------------------------

from fastapi.responses import JSONResponse

@app.post("/login_admin")
async def login_admin(request: Request):
    data = await request.json()

    username = data.get("username")
    password = data.get("password")

    print("LOGIN RICEVUTO:", username, password)

    if username in ADMINS and ADMINS[username] == password:
        print("ACCESSO APPROVATO")

        SESSIONS.add(username)

        # Risposta con cookie
        response = JSONResponse({"status": "ok"})
        response.set_cookie(
            key="admin_user",
            value=username,
            httponly=True,
            secure=False,
            samesite="strict"
        )

        return response

    else:
        print("CREDENZIALI SBAGLIATE")
        return {"status": "error", "reason": "Credenziali non valide"}
