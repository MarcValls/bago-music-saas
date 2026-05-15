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

# --- Models ---
class InventoryRequest(BaseModel):
    xml: str
    target: str = "all"

class TransposeRequest(BaseModel):
    xml: str
    target: str
    semitones: int
    interval: str = None

class ValidateRequest(BaseModel):
    original: str
    transposed: str
    target: str
    semitones: int

# --- Tier checking ---
def check_tier(api_key: str) -> str:
    tiers = {
        "bago_free": "free",
        "bago_pro": "pro",
        "bago_studio": "studio",
    }
    return tiers.get(api_key, "free")

# --- Endpoints ---
@app.get("/api/state")
def get_state():
    return {"ok": True, "version": "1.0.0", "mode": "saas"}

@app.post("/api/music/inventory")
def music_inventory(req: InventoryRequest, request: Request):
    api_key = request.headers.get("x-api-key", "")
    tier = check_tier(api_key)
    # Parse MusicXML locally
    try:
        parts = []
        staves = req.xml.count("<score-part")
        parts_count = req.xml.count("<part id=")
        measures = req.xml.count("<measure ")
        notes = req.xml.count("<pitch>")
        # Simple part extraction
        import re
        part_names = re.findall(r'<part-name>([^<]+)</part-name>', req.xml)
        part_ids = re.findall(r'<score-part id="([^"]+)"', req.xml)
        parts = [{"id": pid, "name": pname} for pid, pname in zip(part_ids, part_names)]
        if not parts:
            parts = [{"id": "P1", "name": "Part 1"}]
        return {
            "ok": True,
            "tier": tier,
            "parts": parts,
            "stats": {"measures": measures, "notes": notes, "parts": len(parts)},
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/music/transpose")
def music_transpose(req: TransposeRequest, request: Request):
    api_key = request.headers.get("x-api-key", "")
    tier = check_tier(api_key)
    if tier == "free":
        raise HTTPException(403, "Transposición requiere plan Pro o Studio")
    try:
        # Use existing pipeline
        import musicxml_transpose
        result = musicxml_transpose.transpose_part(
            req.xml, req.target, req.semitones
        )
        return {"ok": True, "xml": result, "tier": tier}
    except Exception as e:
        # Fallback: return error so client uses local
        return {"ok": False, "error": str(e), "tier": tier}

@app.post("/api/music/validate")
def music_validate(req: ValidateRequest, request: Request):
    api_key = request.headers.get("x-api-key", "")
    tier = check_tier(api_key)
    try:
        orig_notes = req.original.count("<pitch>")
        trans_notes = req.transposed.count("<pitch>")
        match = orig_notes == trans_notes
        warnings = []
        errors = []
        if not match:
            warnings.append(f"Diferencia en conteo: {orig_notes} → {trans_notes}")
        return {
            "ok": match,
            "message": "Validación completada" if match else "Diferencias detectadas",
            "warnings": warnings,
            "errors": errors,
            "tier": tier,
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/taberna_galactica.xml")
def taberna_xml():
    path = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "musicxml" / "taberna_galactica.xml"
    if path.exists():
        return {"xml": path.read_text(encoding="utf-8")}
    # Fallback: generate minimal
    return {"xml": "<?xml version=\"1.0\"?><score-partwise></score-partwise>"}

# --- Static files (web apps) ---
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


# --- Stripe integration ---
import stripe
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

@app.get("/api/pricing")
def get_pricing():
    return {
        "tiers": [
            {"id": "free", "name": "Free", "price": 0, "features": ["3 transposiciones/mes", "Export MusicXML"]},
            {"id": "pro", "name": "Pro", "price": 4.99, "currency": "EUR", "features": ["Transposiciones ilimitadas", "Export PDF/SVG/PNG", "Validación avanzada"]},
            {"id": "studio", "name": "Studio", "price": 14.99, "currency": "EUR", "features": ["Todo Pro", "Ableton integration", "MIDI export", "API access"]},
        ]
    }

@app.post("/api/checkout")
def create_checkout(request: Request):
    data = request.json()
    tier = data.get("tier", "pro")
    price_id = os.environ.get(f"STRIPE_PRICE_{tier.upper()}", "")
    if not price_id:
        raise HTTPException(400, "Price ID not configured")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url="https://bago-music.app/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://bago-music.app/cancel",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/verify")
def verify_session(request: Request):
    data = request.json()
    session_id = data.get("session_id")
    if not session_id:
        raise HTTPException(400, "Missing session_id")
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            # Return API key based on tier
            tier = "pro" if "pro" in session.metadata else "studio"
            return {"ok": True, "tier": tier, "api_key": f"bago_{tier}"}
        return {"ok": False}
    except Exception as e:
        raise HTTPException(500, str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7430)

