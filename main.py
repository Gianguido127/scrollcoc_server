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

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>ScrollCoC Admin Panel</title>
    <style>
        :root {
            --bg: #0f172a;
            --bg-card: #1e293b;
            --bg-card-soft: #111827;
            --text: #e5e7eb;
            --accent: #3b82f6;
            --accent-soft: #1d4ed8;
            --danger: #ef4444;
            --border: #334155;
            --muted: #9ca3af;
            --success: #22c55e;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 24px;
        }
        .page {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        .title {
            font-size: 24px;
            font-weight: 700;
        }
        .subtitle {
            font-size: 14px;
            color: var(--muted);
            margin-top: 4px;
        }
        .toggle-dark {
            padding: 8px 14px;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: var(--bg-card);
            color: var(--text);
            cursor: pointer;
            font-size: 13px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1.2fr 1.8fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: var(--bg-card);
            border-radius: 14px;
            border: 1px solid var(--border);
            padding: 16px 18px;
            box-shadow: 0 18px 40px rgba(15,23,42,0.7);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .card-title {
            font-size: 16px;
            font-weight: 600;
        }
        .card-subtitle {
            font-size: 12px;
            color: var(--muted);
        }
        .btn {
            padding: 7px 14px;
            border-radius: 999px;
            border: none;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .btn-primary {
            background: var(--accent);
            color: white;
        }
        .btn-primary:hover {
            background: var(--accent-soft);
        }
        .btn-outline {
            background: transparent;
            color: var(--text);
            border: 1px solid var(--border);
        }
        .btn-outline:hover {
            border-color: var(--accent);
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            background: var(--bg-card-soft);
            border: 1px solid var(--border);
            font-size: 12px;
            color: var(--muted);
        }
        .badge-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: var(--success);
        }
        .stat-number {
            font-size: 28px;
            font-weight: 700;
            margin-top: 8px;
        }
        .stat-label {
            font-size: 12px;
            color: var(--muted);
        }
        .table-wrapper {
            margin-top: 10px;
            border-radius: 10px;
            border: 1px solid var(--border);
            overflow: hidden;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        thead {
            background: #020617;
        }
        th, td {
            padding: 8px 10px;
            text-align: left;
        }
        th {
            font-weight: 500;
            color: var(--muted);
            border-bottom: 1px solid var(--border);
        }
        tbody tr:nth-child(odd) {
            background: #020617;
        }
        tbody tr:nth-child(even) {
            background: #030712;
        }
        tbody tr:hover {
            background: #0b1120;
        }
        .search-row {
            display: flex;
            gap: 10px;
            margin-top: 8px;
            margin-bottom: 8px;
        }
        .input {
            flex: 1;
            padding: 7px 10px;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: var(--bg-card-soft);
            color: var(--text);
            font-size: 13px;
        }
        .input::placeholder {
            color: var(--muted);
        }
        .pagination {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 8px;
            font-size: 12px;
            color: var(--muted);
        }
        .log {
            margin-top: 10px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: #020617;
            padding: 8px 10px;
            font-size: 12px;
            max-height: 160px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        .progress-bar {
            width: 100%;
            height: 6px;
            border-radius: 999px;
            background: #020617;
            overflow: hidden;
            margin-top: 8px;
        }
        .progress-inner {
            height: 100%;
            width: 0%;
            background: var(--accent);
            transition: width 0.2s ease-out;
        }
        .spinner {
            width: 14px;
            height: 14px;
            border-radius: 999px;
            border: 2px solid rgba(148,163,184,0.4);
            border-top-color: var(--accent);
            animation: spin 0.7s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .muted {
            color: var(--muted);
            font-size: 12px;
        }
        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            background: #020617;
            border: 1px solid var(--border);
            font-size: 11px;
            color: var(--muted);
        }
        .pill-dot {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            background: var(--accent);
        }
        .footer {
            margin-top: 18px;
            font-size: 11px;
            color: var(--muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .link {
            color: var(--accent);
            text-decoration: none;
            font-size: 11px;
        }
        .link:hover {
            text-decoration: underline;
        }
        .hidden { display: none; }
        .text-danger { color: var(--danger); }
        .text-success { color: var(--success); }
    </style>
</head>
<body>
<div class="page">
    <div class="header">
        <div>
            <div class="title">ScrollCoC Admin Panel</div>
            <div class="subtitle">Controllo e ispezione del database shorts direttamente dal server.</div>
        </div>
        <button class="toggle-dark" id="toggleDark">
            🌗 Dark mode
        </button>
    </div>

    <div class="grid">
        <!-- STATS CARD -->
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Statistiche database</div>
                    <div class="card-subtitle">Conteggio totale dei link presenti in <code>links.json</code>.</div>
                </div>
                <button class="btn btn-outline" id="refreshCountBtn">
                    <span id="countSpinner" class="spinner hidden"></span>
                    Aggiorna conteggio
                </button>
            </div>
            <div>
                <div class="stat-number" id="totalCount">–</div>
                <div class="stat-label" id="countLabel">In attesa di aggiornamento…</div>
                <div style="margin-top:10px;">
                    <span class="badge">
                        <span class="badge-dot"></span>
                        <span id="lastCountTime">Mai aggiornato</span>
                    </span>
                </div>
            </div>
        </div>

        <!-- UPDATE CARD -->
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="card-title">Aggiorna database</div>
                    <div class="card-subtitle">Esegue l’update server-side dei shorts (versione integrata di auto_update_shorts.py).</div>
                </div>
                <button class="btn btn-primary" id="updateDbBtn">
                    <span id="updateSpinner" class="spinner hidden"></span>
                    Aggiorna database
                </button>
            </div>
            <div>
                <div class="progress-bar">
                    <div class="progress-inner" id="updateProgress"></div>
                </div>
                <div class="muted" id="updateStatus" style="margin-top:6px;">
                    Nessun aggiornamento in corso.
                </div>
                <div class="log" id="updateLog"></div>
            </div>
        </div>
    </div>

    <!-- DATABASE VIEWER -->
    <div class="card">
        <div class="card-header">
            <div>
                <div class="card-title">Database viewer</div>
                <div class="card-subtitle">Visualizza i link presenti nel database con paginazione e ricerca interna.</div>
            </div>
            <button class="btn btn-outline" id="refreshTableBtn">
                <span id="tableSpinner" class="spinner hidden"></span>
                Aggiorna tabella
            </button>
        </div>

        <div class="search-row">
            <input class="input" id="searchInput" placeholder="Filtra per ID (ricerca locale nella pagina)…">
            <span class="pill">
                <span class="pill-dot"></span>
                Pagina <span id="pageInfo">1 / –</span>
            </span>
        </div>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width:40px;">#</th>
                        <th>ID</th>
                    </tr>
                </thead>
                <tbody id="linksTableBody">
                    <tr><td colspan="2">Nessun dato caricato.</td></tr>
                </tbody>
            </table>
        </div>

        <div class="pagination">
            <div>
                <button class="btn btn-outline" id="prevPageBtn">← Pagina precedente</button>
                <button class="btn btn-outline" id="nextPageBtn">Pagina successiva →</button>
            </div>
            <div>
                <span class="muted" id="paginationInfo">0 elementi mostrati.</span>
            </div>
        </div>
    </div>

    <div class="footer">
        <span>ScrollCoC Admin • controllo diretto del database shorts.</span>
        <span>Endpoint: <a class="link" href="/api/links" target="_blank">/api/links</a></span>
    </div>
</div>

<script>
(function() {
    const API_BASE = "";

    let currentPage = 1;
    let totalPages = 1;
    const limit = 200;
    let currentLinks = [];

    const totalCountEl = document.getElementById("totalCount");
    const countLabelEl = document.getElementById("countLabel");
    const lastCountTimeEl = document.getElementById("lastCountTime");
    const countSpinnerEl = document.getElementById("countSpinner");

    const updateDbBtn = document.getElementById("updateDbBtn");
    const updateSpinnerEl = document.getElementById("updateSpinner");
    const updateProgressEl = document.getElementById("updateProgress");
    const updateStatusEl = document.getElementById("updateStatus");
    const updateLogEl = document.getElementById("updateLog");

    const refreshTableBtn = document.getElementById("refreshTableBtn");
    const tableSpinnerEl = document.getElementById("tableSpinner");
    const linksTableBodyEl = document.getElementById("linksTableBody");
    const paginationInfoEl = document.getElementById("paginationInfo");
    const pageInfoEl = document.getElementById("pageInfo");
    const prevPageBtn = document.getElementById("prevPageBtn");
    const nextPageBtn = document.getElementById("nextPageBtn");
    const searchInputEl = document.getElementById("searchInput");

    const toggleDarkBtn = document.getElementById("toggleDark");

    function nowString() {
        const d = new Date();
        return d.toLocaleString("it-IT");
    }

    async function fetchCount() {
        countSpinnerEl.classList.remove("hidden");
        try {
            const res = await fetch(API_BASE + "/admin/count");
            const data = await res.json();
            totalCountEl.textContent = data.count ?? "0";
            countLabelEl.textContent = "Conteggio aggiornato.";
            lastCountTimeEl.textContent = "Ultimo aggiornamento: " + nowString();
        } catch (e) {
            countLabelEl.textContent = "Errore nel conteggio.";
        } finally {
            countSpinnerEl.classList.add("hidden");
        }
    }

    async function fetchLinks(page) {
        tableSpinnerEl.classList.remove("hidden");
        try {
            const res = await fetch(API_BASE + `/admin/get_all_links?page=${page}&limit=${limit}`);
            const data = await res.json();
            currentPage = data.page;
            totalPages = data.total_pages;
            currentLinks = data.links || [];
            renderTable();
        } catch (e) {
            linksTableBodyEl.innerHTML = '<tr><td colspan="2">Errore nel caricamento dei dati.</td></tr>';
        } finally {
            tableSpinnerEl.classList.add("hidden");
        }
    }

    function renderTable() {
        const filter = searchInputEl.value.trim().toLowerCase();
        let filtered = currentLinks;
        if (filter) {
            filtered = currentLinks.filter(item => (item.id || "").toLowerCase().includes(filter));
        }

        if (!filtered.length) {
            linksTableBodyEl.innerHTML = '<tr><td colspan="2">Nessun elemento trovato.</td></tr>';
        } else {
            linksTableBodyEl.innerHTML = filtered.map((item, idx) => {
                const index = (idx + 1);
                const id = item.id || "";
                return `<tr>
                    <td>${index}</td>
                    <td><code>${id}</code></td>
                </tr>`;
            }).join("");
        }

        paginationInfoEl.textContent = `${filtered.length} elementi mostrati in questa pagina.`;
        pageInfoEl.textContent = `${currentPage} / ${totalPages}`;
    }

    async function updateDatabase() {
        updateSpinnerEl.classList.remove("hidden");
        updateStatusEl.textContent = "Aggiornamento in corso…";
        updateLogEl.textContent = "";
        updateProgressEl.style.width = "0%";

        let progress = 0;
        const interval = setInterval(() => {
            progress = Math.min(100, progress + 7);
            updateProgressEl.style.width = progress + "%";
        }, 200);

        try {
            const res = await fetch(API_BASE + "/admin/update_database", {
                method: "POST"
            });
            const data = await res.json();
            clearInterval(interval);
            updateProgressEl.style.width = "100%";

            updateStatusEl.textContent = "Aggiornamento completato.";
            updateLogEl.textContent =
                "Status: " + (data.status || "unknown") + "\\n" +
                "Messaggio: " + (data.message || "") + "\\n" +
                "Aggiunti: " + (data.added ?? "–") + "\\n" +
                "Totale: " + (data.total ?? "–") + "\\n" +
                "Ora: " + nowString();

            fetchCount();
            fetchLinks(currentPage);
        } catch (e) {
            clearInterval(interval);
            updateProgressEl.style.width = "0%";
            updateStatusEl.textContent = "Errore durante l’aggiornamento.";
            updateLogEl.textContent = "Errore: " + e;
        } finally {
            updateSpinnerEl.classList.add("hidden");
        }
    }

    function toggleDark() {
        document.body.classList.toggle("light-mode");
        if (document.body.classList.contains("light-mode")) {
            document.documentElement.style.setProperty("--bg", "#f3f4f6");
            document.documentElement.style.setProperty("--bg-card", "#ffffff");
            document.documentElement.style.setProperty("--bg-card-soft", "#e5e7eb");
            document.documentElement.style.setProperty("--text", "#0f172a");
            document.documentElement.style.setProperty("--border", "#d1d5db");
            document.documentElement.style.setProperty("--muted", "#6b7280");
        } else {
            document.documentElement.style.setProperty("--bg", "#0f172a");
            document.documentElement.style.setProperty("--bg-card", "#1e293b");
            document.documentElement.style.setProperty("--bg-card-soft", "#111827");
            document.documentElement.style.setProperty("--text", "#e5e7eb");
            document.documentElement.style.setProperty("--border", "#334155");
            document.documentElement.style.setProperty("--muted", "#9ca3af");
        }
    }

    refreshCountBtn.addEventListener("click", fetchCount);
    refreshTableBtn.addEventListener("click", () => fetchLinks(currentPage));
    updateDbBtn.addEventListener("click", updateDatabase);
    prevPageBtn.addEventListener("click", () => {
        if (currentPage > 1) {
            fetchLinks(currentPage - 1);
        }
    });
    nextPageBtn.addEventListener("click", () => {
        if (currentPage < totalPages) {
            fetchLinks(currentPage + 1);
        }
    });
    searchInputEl.addEventListener("input", renderTable);
    toggleDarkBtn.addEventListener("click", toggleDark);

    fetchCount();
    fetchLinks(1);
})();
</script>
</body>
</html>
"""


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return ADMIN_HTML
