from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json
from pathlib import Path

app = FastAPI()

# Monta la cartella static (serve links.json e altri file)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Homepage → restituisce index.html
@app.get("/")
def home():
    return FileResponse("index.html")

# API → restituisce il contenuto di links.json
@app.get("/api/links")
def get_links():
    path = Path("static/links.json")
    if not path.exists():
        return JSONResponse([], status_code=200)

    with open(path, "r") as f:
        data = json.load(f)

    return JSONResponse(data)

from pydantic import BaseModel

class LinksPayload(BaseModel):
    data: list

@app.put("/update_links")
def update_links(payload: LinksPayload):
    path = Path("static/links.json")
    with open(path, "w") as f:
        json.dump(payload.data, f, indent=4)
    return {"status": "ok"}
