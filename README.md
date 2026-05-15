# BAGO Music SaaS

Backend + PWA para transposición de partituras.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/MarcValls/bago-music-saas)

## Deploy (1 clic)

1. Clic en **"Deploy to Render"** arriba ↑
2. Render pedirá crear cuenta (gratis)
3. Selecciona el plan **Free**
4. Espera 2-3 minutos
5. Copia la URL del servicio

## Configurar webhook de Telegram

```bash
python setup_webhook.py https://TU-URL.onrender.com
```

O manualmente:
```bash
curl -X POST "https://api.telegram.org/bot8519892399:AAHTKzfu_VyLUSpJ-iNjmSn9RcgFOsddeKA/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://TU-URL.onrender.com/webhook"}'
```

## PWA

https://marcvalls.github.io/bago-music-saas/

## APK

Build automático en GitHub Actions:
https://github.com/MarcValls/bago-music-saas/actions
