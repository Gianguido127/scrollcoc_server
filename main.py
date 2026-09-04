from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, RedirectResponse
import json
from pathlib import Path
import secrets
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

# ---------------------------
# CONFIGURAZIONE ADMIN
# ---------------------------

ADMINS = {
    "superadmin": "Juve1897$",
}

PENDING_APPROVAL = {}  # username → token
SESSIONS = set()       # utenti loggati e approvati

SUPERADMIN_EMAIL = "tommycangy@gmail.com"  
SMTP_USER = "superadminscrollcoc@gmail.com"         
SMTP_PASS = "yvyxtrcgvijlypxs"        


# ---------------------------
# FUNZIONE INVIO EMAIL
# ---------------------------

def send_email_to_superadmin(subject, body):
    print("Sto provando a inviare la mail...")
    print("SMTP PASS:", SMTP_PASS)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = SUPERADMIN_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, SUPERADMIN_EMAIL, msg.as_string())

    print("Mail inviata dal server FastAPI")

# ---------------------------
# HOMEPAGE
# ---------------------------

@app.get("/")
def home():
    return FileResponse("index.html")


# ---------------------------
# API LINKS (normale)
# ---------------------------

@app.get("/api/links")
def get_links():
    path = Path("links.json")
    if not path.exists():
        return []

    with open(path, "r") as f:
        data = json.load(f)

    return data


# ---------------------------
# UPDATE LINKS
# ---------------------------

@app.put("/update_links")
async def update_links(request: Request):
    path = Path("links.json")

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"status": "error", "reason": "Invalid JSON"}, status_code=400)

    if not isinstance(payload, dict):
        return JSONResponse({"status": "error", "reason": "Payload must be a dict"}, status_code=400)

    if "data" not in payload or not isinstance(payload["data"], list):
        return JSONResponse({"status": "error", "reason": "'data' must be a list"}, status_code=400)

    new_data = payload["data"]

    existing = []
    if path.exists():
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    existing = data
        except Exception:
            existing = []

    combined = existing + new_data

    seen = set()
    unique = []
    for item in combined:
        marker = json.dumps(item, sort_keys=True)
        if marker not in seen:
            seen.add(marker)
            unique.append(item)

    try:
        with open(path, "w") as f:
            json.dump(unique, f, indent=4)
    except Exception as e:
        return JSONResponse({"status": "error", "reason": f"write_failed: {str(e)}"}, status_code=500)

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
# LOGIN ADMIN → RICHIESTA APPROVAZIONE
# ---------------------------

@app.post("/login_admin")
async def login_admin(request: Request):
    data = await request.json()

    username = data.get("username")
    password = data.get("password")

    print("LOGIN RICEVUTO:", username, password)
    
    if username in ADMINS and ADMINS[username] == password:
        print("CREDENZIALI CORRETTE, INVIO MAIL...")

        # genera token
        token = secrets.token_hex(16)
        PENDING_APPROVAL[username] = token

        # invia email al superadmin
        approve_link = f"https://scrollcoc-server.onrender.com/approve_admin?user={username}&token={token}"

        send_email_to_superadmin(
            subject="Richiesta accesso admin",
            body=f"""
L'utente {username} sta tentando di accedere alla pagina admin.

Approva l'accesso cliccando qui:
{approve_link}
"""
        )

        return JSONResponse({
            "status": "waiting",
            "message": "In attesa di conferma dal superadmin..."
        })

    return {"status": "error", "reason": "Credenziali non valide"}


# ---------------------------
# APPROVAZIONE SUPERADMIN
# ---------------------------

@app.get("/approve_admin")
def approve_admin(user: str, token: str):
    if user in PENDING_APPROVAL and PENDING_APPROVAL[user] == token:
        del PENDING_APPROVAL[user]
        SESSIONS.add(user)

        response = RedirectResponse("/t1m2s7")
        response.set_cookie("admin_user", user, max_age=3600)
        return response

    return HTMLResponse("Token non valido.")


# ---------------------------
# CHECK APPROVAL (polling)
# ---------------------------

@app.get("/check_approval")
def check_approval(user: str):
    return {"approved": user in SESSIONS}
