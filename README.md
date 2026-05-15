# BAGO Music SaaS

Backend + PWA para transposición de partituras.

## Deploy en Render.com (gratis)

1. Ve a [dashboard.render.com](https://dashboard.render.com)
2. Clic en **"New +"** → **"Web Service"**
3. Conecta tu repo `MarcValls/bago-music-saas`
4. Render detectará `render.yaml` automáticamente
5. Clic en **"Create Web Service"**
6. Espera 2-3 minutos a que deploye
7. Copia la URL (ej: `https://bago-music-saas-xxx.onrender.com`)

## Configurar webhook de Telegram

Ejecuta en tu terminal:
```bash
python setup_webhook.py https://bago-music-saas-xxx.onrender.com
```

O manualmente:
```bash
curl -X POST "https://api.telegram.org/bot8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://bago-music-saas-xxx.onrender.com/webhook"}'
```

## PWA

https://marcvalls.github.io/bago-music-saas/

## APK

Build automático en GitHub Actions:
https://github.com/MarcValls/bago-music-saas/actions
