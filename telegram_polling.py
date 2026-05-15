import requests, subprocess, time

TOKEN = "8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA"
API = "https://api.telegram.org/bot" + TOKEN
offset = 0
BAGO = r"C:\Users\AMTEC_Terminal_1º\BAGO"

print("[BOT] Iniciando polling...", flush=True)

for i in range(100):  # 100 iteraciones = ~200s de prueba
    try:
        r = requests.get(API + "/getUpdates", params={"offset": offset, "limit": 5}, timeout=15)
        data = r.json()
        if data.get("ok") and data.get("result"):
            for u in data["result"]:
                offset = max(offset, u["update_id"] + 1)
                msg = u.get("message")
                if not msg:
                    continue
                text = msg.get("text", "").strip()
                chat = msg["chat"]["id"]
                user = msg["from"].get("first_name", "?")
                print(f"[BOT] {user}: {text}", flush=True)
                
                # Ejecutar BAGO
                try:
                    result = subprocess.run(
                        ["powershell", "-ExecutionPolicy", "Bypass", "-File", BAGO + "\\bago.ps1"] + text.split(),
                        capture_output=True, text=True, timeout=45, cwd=BAGO
                    )
                    reply = (result.stdout or result.stderr or "OK").strip()[:3500]
                except Exception as e:
                    reply = f"Error: {e}"
                
                # Responder
                try:
                    requests.post(API + "/sendMessage", json={"chat_id": chat, "text": reply}, timeout=15)
                    print(f"[BOT] Replied", flush=True)
                except Exception as e:
                    print(f"[BOT] Send err: {e}", flush=True)
    except Exception as e:
        print(f"[BOT] Poll err: {e}", flush=True)
    
    time.sleep(2)

print("[BOT] Terminado", flush=True)
