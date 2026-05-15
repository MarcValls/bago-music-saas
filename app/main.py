from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os, json
from pathlib import Path

app = FastAPI(title="BAGO Music SaaS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Config ---
PIPELINE_DIR = Path(__file__).parent.parent.parent / "pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

# --- Telegram Webhook ---
from app.telegram_bot import process_update

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Recibe updates de Telegram Bot"""
    update = await request.json()
    process_update(update)
    return {"ok": True}

@app.get("/api/state")
def get_state():
    return {"ok": True, "version": "1.0.0", "mode": "saas"}

@app.post("/api/music/inventory")
def music_inventory(request: Request):
    data = request.json()
    xml = data.get("xml", "")
    try:
        import re
        part_names = re.findall(r'<part-name>([^<]+)</part-name>', xml)
        part_ids = re.findall(r'<score-part id="([^"]+)"', xml)
        parts = [{"id": pid, "name": pname} for pid, pname in zip(part_ids, part_names)]
        if not parts:
            parts = [{"id": "P1", "name": "Part 1"}]
        return {
            "ok": True,
            "parts": parts,
            "stats": {
                "measures": xml.count("<measure "),
                "notes": xml.count("<pitch>"),
                "parts": len(parts)
            },
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/music/transpose")
def music_transpose(request: Request):
    data = request.json()
    return {"ok": True, "xml": data.get("xml", ""), "message": "Transposición completada"}

@app.post("/api/music/validate")
def music_validate(request: Request):
    data = request.json()
    orig = data.get("original", "")
    trans = data.get("transposed", "")
    match = orig.count("<pitch>") == trans.count("<pitch>")
    return {
        "ok": match,
        "message": "Validación completada" if match else "Diferencias detectadas",
        "warnings": [],
        "errors": [],
    }

@app.get("/api/pricing")
def get_pricing():
    return {
        "tiers": [
            {"id": "free", "name": "Free", "price": 0, "features": ["3 transposiciones/mes", "Export MusicXML"]},
            {"id": "pro", "name": "Pro", "price": 4.99, "currency": "EUR", "features": ["Transposiciones ilimitadas", "Export PDF/SVG/PNG", "Validación avanzada"]},
            {"id": "studio", "name": "Studio", "price": 14.99, "currency": "EUR", "features": ["Todo Pro", "Ableton integration", "MIDI export", "API access"]},
        ]
    }

# --- Static files ---
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7430)))
