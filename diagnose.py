import requests, json, sys

# Verificar webhook
TOKEN = "8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA"
API = f"https://api.telegram.org/bot{TOKEN}"

print("=== DIAGNOSTICO BAGO Music ===")
print()

# 1. Verificar webhook
r = requests.get(f"{API}/getWebhookInfo")
info = r.json()
print("1. Webhook configurado:", info["result"]["url"])
print("   Updates pendientes:", info["result"]["pending_update_count"])
print("   Ultimo error:", info["result"].get("last_error_message", "Ninguno"))
print()

# 2. Verificar servidor
SERVER = "https://bago-music-saas.onrender.com"
print(f"2. Probando servidor: {SERVER}")
try:
    r2 = requests.get(f"{SERVER}/api/state", timeout=15)
    print(f"   Status: {r2.status_code}")
    print(f"   Respuesta: {r2.json()}")
except Exception as e:
    print(f"   ERROR: {e}")
print()

# 3. Verificar bot
r3 = requests.get(f"{API}/getMe")
me = r3.json()
print("3. Bot:", me["result"]["username"])
print("   Activo:", me["ok"])
