import requests, sys

TOKEN = "8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA"
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else input("URL del servidor (ej: https://bago-music-saas.onrender.com): ").strip()
WEBHOOK_URL = f"{BASE_URL}/webhook"

print(f"Configurando webhook: {WEBHOOK_URL}")
r = requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", json={"url": WEBHOOK_URL})
print("setWebhook:", r.json())

r2 = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
print("getWebhookInfo:", r2.json())
