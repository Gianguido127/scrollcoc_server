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

# UPDATE → salva links.json nella root
@app.put("/update_links")
def update_links(payload: LinksPayload):
    path = Path("links.json")
    with open(path, "w") as f:
        json.dump(payload.data, f, indent=4)
    return {"status": "ok"}
