# BAGO Music SaaS

## Deploy en 2 minutos

### Opcion 1: Render.com (Gratis, recomendado)

1. Ve a https://render.com
2. Registrate con GitHub
3. New + → Web Service
4. Conecta repo: `MarcValls/bago-music-saas`
5. Plan: Free
6. Build Command: `pip install -r requirements.txt`
7. Start Command: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`
8. Environment Variables:
   - `BAGO_TELEGRAM_TOKEN` = `8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA`
9. Create Web Service
10. Espera 2 minutos
11. Copia tu URL: `https://bago-music-saas-xxx.onrender.com`

### Configurar webhook Telegram

```bash
python setup_webhook.py https://TU-URL.onrender.com
```

O manualmente:
```bash
curl -X POST "https://api.telegram.org/bot8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://TU-URL.onrender.com/webhook"}'
```

### Opcion 2: Docker local

```bash
cd saas
docker-compose up --build
```

### Opcion 3: Ejecutar local (para bot Telegram)

```bash
cd saas
python -m uvicorn app.main:app --host 127.0.0.1 --port 7430
```

Luego configura el webhook con ngrok/localtunnel.

## PWA

https://marcvalls.github.io/bago-music-saas/

## APK

Build en GitHub Actions: https://github.com/MarcValls/bago-music-saas/actions
