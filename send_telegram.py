import requests
import sys

TOKEN = "8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA"
CHAT_ID = "MarcValls"  # O usar tu chat_id real

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    r = requests.post(url, json=payload, timeout=30)
    print(r.json())

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "Mensaje de BAGO"
    send_message(msg)
