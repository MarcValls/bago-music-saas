import requests, sys

TOKEN = "8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA"
WEBHOOK_URL = sys.argv[1] if len(sys.argv) > 1 else "https://bago-music-saas.onrender.com/webhook"

# Set webhook
r = requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", json={"url": WEBHOOK_URL})
print(r.json())

# Get webhook info
r2 = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
print(r2.json())
