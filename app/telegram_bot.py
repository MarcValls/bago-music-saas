"""BAGO Telegram Bot — webhook handler para Render.com"""
import json, os, subprocess, tempfile
from pathlib import Path

TOKEN = os.environ.get("BAGO_TELEGRAM_TOKEN", "8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA")
API = f"https://api.telegram.org/bot{TOKEN}"

import requests

def send_message(chat_id, text):
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text[:4000],
            "parse_mode": "HTML"
        }, timeout=30)
    except Exception as e:
        print(f"[ERR send] {e}")

def process_update(update):
    msg = update.get("message")
    if not msg:
        return
    text = msg.get("text", "").strip()
    chat_id = msg["chat"]["id"]
    user = msg["from"].get("first_name", "Usuario")
    
    print(f"[BOT] {user}: {text}")
    
    if text.startswith("/start"):
        send_message(chat_id,
            "🎵 <b>BAGO Music</b>\n\n"
            "Tu asistente musical en la nube.\n\n"
            "<b>Comandos:</b>\n"
            "• /status — Estado del servicio\n"
            "• /transponer — Info de transposición\n"
            "• /precios — Planes de suscripción\n"
            "• /apk — Estado del build APK\n"
            "• /help — Ayuda\n\n"
            "Web: https://marcvalls.github.io/bago-music-saas/"
        )
        return
    
    if text.startswith("/help"):
        send_message(chat_id,
            "<b>Comandos disponibles:</b>\n"
            "• /start — Bienvenida\n"
            "• /status — Estado del servicio\n"
            "• /transponer — Herramienta de transposición\n"
            "• /precios — Planes Free/Pro/Studio\n"
            "• /apk — Descargar APK\n"
            "• Texto libre — Lo procesaré como tarea"
        )
        return
    
    if text.startswith("/status"):
        send_message(chat_id,
            "✅ <b>BAGO Music SaaS</b> activo\n\n"
            "• Backend: ONLINE\n"
            "• PWA: https://marcvalls.github.io/bago-music-saas/\n"
            "• Pipeline: MusicXML ready\n"
            "• Stripe: Configurado\n\n"
            "Escribe /precios para ver planes."
        )
        return
    
    if text.startswith("/precios"):
        send_message(chat_id,
            "💰 <b>Planes BAGO Music</b>\n\n"
            "🆓 <b>Free</b> — €0/mes\n"
            "  • 3 transposiciones/mes\n"
            "  • Export MusicXML\n\n"
            "⭐ <b>Pro</b> — €4.99/mes\n"
            "  • Transposiciones ilimitadas\n"
            "  • Export PDF/SVG/PNG\n"
            "  • Validación avanzada\n\n"
            "🎛️ <b>Studio</b> — €14.99/mes\n"
            "  • Todo Pro\n"
            "  • Ableton integration\n"
            "  • MIDI export + API access\n\n"
            "Upgrade: /checkout pro"
        )
        return
    
    if text.startswith("/apk"):
        send_message(chat_id,
            "📱 <b>BAGO Music APK</b>\n\n"
            "La app se instala como PWA desde:\n"
            "https://marcvalls.github.io/bago-music-saas/\n\n"
            "En Android:\n"
            "1. Abre en Chrome\n"
            "2. ⋮ → 'Añadir a pantalla de inicio'\n"
            "3. Se instala como app nativa\n\n"
            "Build en progreso en GitHub Actions:\n"
            "https://github.com/MarcValls/bago-music-saas/actions"
        )
        return
    
    if text.startswith("/transponer"):
        send_message(chat_id,
            "🎼 <b>Transposición</b>\n\n"
            "Abre la web para transponer partituras:\n"
            "https://marcvalls.github.io/bago-music-saas/bago_score_teacher.html\n\n"
            "Soporta MusicXML, MIDI, PDF.\n"
            "Elige partitura → selecciona voz → transponer."
        )
        return
    
    # Mensaje libre
    send_message(chat_id,
        f"📝 Recibido: <i>{text}</i>\n\n"
        "Para acciones usa:\n"
        "• /transponer — Ir a la app\n"
        "• /status — Ver estado\n"
        "• /precios — Ver planes"
    )
