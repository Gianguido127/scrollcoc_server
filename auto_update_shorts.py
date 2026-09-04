import requests
import json
import os
import time
import random
import string
import re


# ============================================================
# FUNZIONE DI RICHIESTA SICURA (ANTI-BLOCCO YOUTUBE)
# ============================================================

def safe_get(url, retries=5, delay=1):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r
            print(f"Status {r.status_code} da YouTube, retry...")
        except Exception as e:
            print(f"Errore ({i+1}/{retries}) su {url}: {e}")
        time.sleep(delay)
    print(f"ERRORE FATALE: impossibile raggiungere {url}")
    return None


# ============================================================
# RACCOLTA SHORTS
# ============================================================

shorts_ids = set()

def add_short(video_id):
    if len(video_id) == 11:
        shorts_ids.add(video_id)


# ============================================================
# RICERCHE MIRATE 
# ============================================================

SEARCH_KEYWORDS = [
    "funny shorts", "viral shorts", "best shorts", "challenge shorts",
    "meme shorts", "football shorts", "gaming shorts", "italy shorts",
    "tiktok shorts", "compilation shorts", "shorts", "Ronaldo",
    "SkibidiToilet", "viral", "tiktok", "Italia", "Virale",
    "tiktok italia", "gaming", "music", "dazn", "news", "la zanzara",
    "politica", "calcio", "meme", "intrattenimento", "notizie", "novità",
    "divertente", "schetch", "comici", "film", "marvel", "curiosità",
    "lo sapevi che", "storia", "geografia", "geopop", "scienza",
    "67", "aura", "skibid", "pantellas", "barbari", "the bisseohls",
    "serie a", "magia", "messi", "tv", "ball"
]

def fetch_keyword_search():
    for kw in SEARCH_KEYWORDS:
        print(f"Ricerca shorts: {kw}")
        url = f"https://www.youtube.com/results?search_query={kw.replace(' ', '+')}"
        r = safe_get(url)
        if not r:
            continue
        matches = re.findall(r"/shorts/([A-Za-z0-9_-]{11})", r.text)
        for vid in matches:
            add_short(vid)


# ============================================================
# RICERCHE PER LETTERE
# ============================================================

def fetch_letter_search():
    for letter in string.ascii_lowercase:
        print(f"Ricerca shorts per lettera: {letter}")
        url = f"https://www.youtube.com/results?search_query={letter}+shorts"
        r = safe_get(url)
        if not r:
            continue
        matches = re.findall(r"/shorts/([A-Za-z0-9_-]{11})", r.text)
        for vid in matches:
            add_short(vid)


# ============================================================
# RICERCHE PER NUMERI
# ============================================================

def fetch_number_search():
    for num in range(10, 101):
        print(f"Ricerca shorts per numero: {num}")
        url = f"https://www.youtube.com/results?search_query={num}+shorts"
        r = safe_get(url)
        if not r:
            continue
        matches = re.findall(r"/shorts/([A-Za-z0-9_-]{11})", r.text)
        for vid in matches:
            add_short(vid)


# ============================================================
# RICERCHE PER EMOJI
# ============================================================

EMOJIS = ["😂", "⚽", "🎮", "🔥", "🐶", "😱", "😎", "💀"]

def fetch_emoji_search():
    for emoji in EMOJIS:
        print(f"Ricerca shorts per emoji: {emoji}")
        url = f"https://www.youtube.com/results?search_query={emoji}+shorts"
        r = safe_get(url)
        if not r:
            continue
        matches = re.findall(r"/shorts/([A-Za-z0-9_-]{11})", r.text)
        for vid in matches:
            add_short(vid)


# ============================================================
# SEARCH LISTS (SUPER-AGGRESSIVE)
# ============================================================

ADVANCED_KEYWORDS = []
base = ["shorts", "viral", "funny", "meme", "challenge", "tiktok", "italy", "news", "gaming", "football",
        "funny shorts", "viral shorts", "best shorts", "challenge shorts", "meme shorts", "football shorts",
        "gaming shorts", "italy shorts", "tiktok shorts", "compilation shorts", "shorts", "Ronaldo",
        "SkibidiToilet", "viral", "tiktok", "Italia", "Virale", "tiktok italia", "gaming", "music", "dazn",
        "news", "la zanzara", "politica", "calcio", "meme", "intrattenimento", "notizie", "novità",
        "divertente", "schetch", "comici", "film", "marvel", "curiosità", "lo sapevi che", "storia",
        "geografia", "geopop", "scienza", "67", "aura", "skibid", "pantellas", "barbari", "the bisseohls"]

mods = ["2024", "2025", "2026", "best", "top", "new", "crazy", "wtf", "compilation", "edit", "remix"]

for b in base:
    for m in mods:
        ADVANCED_KEYWORDS.append(f"{b} {m}")

DOUBLE_LETTERS = []
for a in string.ascii_lowercase:
    for b in string.ascii_lowercase:
        DOUBLE_LETTERS.append(f"{a}{b} shorts")

RANDOM_NUMBERS = [f"{random.randint(1,9999)} shorts" for _ in range(100)]

EMOJI_COMBO = []
for e1 in EMOJIS:
    for e2 in EMOJIS:
        EMOJI_COMBO.append(f"{e1}{e2} shorts")

symbols = ["@", "#", "$", "%", "&", "?", "!", "+", "-", "_"]
NOISE = []
for s in symbols:
    NOISE.append(f"{s} shorts")
    NOISE.append(f"{s}{s} shorts")
    NOISE.append(f"{s}{random.choice(symbols)} shorts")

ALL_QUERIES = (
    SEARCH_KEYWORDS +
    ADVANCED_KEYWORDS +
    DOUBLE_LETTERS +
    RANDOM_NUMBERS +
    EMOJI_COMBO +
    NOISE
)


# ============================================================
# SUPER-AGGRESSIVE SEARCH FUNCTION
# ============================================================

def fetch_super_aggressive():
    for kw in ALL_QUERIES:
        print(f"Ricerca super-aggressiva: {kw}")
        url = f"https://www.youtube.com/results?search_query={kw.replace(' ', '+')}"
        r = safe_get(url)
        if not r:
            continue
        matches = re.findall(r"/shorts/([A-Za-z0-9_-]{11})", r.text)
        for vid in matches:
            add_short(vid)


# ============================================================
# UPDATE COMPLETO
# ============================================================

def update():

    # CARICA I VECCHI LINK DAL SERVER (NUOVA VERSIONE)
    old_links = set()
    try:
        r = requests.get("https://scrollcoc-server.onrender.com/api/links", timeout=30)
        server_data = r.json()
        for item in server_data:
            old_links.add(item["id"])
        print(f"Vecchi link caricati dal server: {len(old_links)}")
    except Exception as e:
        print("ERRORE nel caricamento dei vecchi link dal server:", e)
        print("Procedo con old_links = 0 (NON IDEALE)")

    # PESCA DA TUTTE LE FONTI
    fetch_super_aggressive()
    fetch_keyword_search()
    fetch_letter_search()
    fetch_number_search()
    fetch_emoji_search()

    # Unisci vecchi + nuovi
    final_links = old_links.union(shorts_ids)

    # Salva tutto
    final = [{"id": vid} for vid in final_links]

    # Spezza in chunk da 500
    chunks = [final[i:i+500] for i in range(0, len(final), 500)]

    for idx, chunk in enumerate(chunks):
        try:
            r = requests.put(
                "https://scrollcoc-server.onrender.com/update_links",
                json={"data": chunk},
                timeout=60
            )
            print(f"CHUNK {idx+1}/{len(chunks)} → SERVER RESPONSE:", r.text)
        except Exception as e:
            print(f"ERRORE nel chunk {idx+1}: {e}")

    print(f"AGGIORNAMENTO COMPLETATO: {len(final)} shorts totali.")


if __name__ == "__main__":
    update()
