import logging, sys, os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("STARTING BAGO Music SaaS")

try:
    app = FastAPI(title="BAGO Music SaaS", version="1.0.0")
    logger.info("FastAPI created")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS added")

    from app.telegram_bot import process_update
    logger.info("Telegram bot imported")

    @app.post("/webhook")
    async def telegram_webhook(request: Request):
        update = await request.json()
        process_update(update)
        return {"ok": True}

    @app.get("/api/state")
    def get_state():
        return {"ok": True, "version": "1.0.0", "mode": "saas"}

    @app.get("/")
    def root():
        return {"name": "BAGO Music", "status": "online", "version": "1.0.0"}

    logger.info("Routes registered")

except Exception as e:
    logger.error(f"FATAL: {e}", exc_info=True)
    raise

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7430))
    logger.info(f"Running on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
