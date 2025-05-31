import os
import logging
from aiohttp import web
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("stoplist")

APP_URL   = os.getenv("APP_URL", "https://iiko-production.up.railway.app")
PORT      = int(os.getenv("PORT", 8080))           # Railway подставит своё значение
STOP_PATH = "/stoplist"                            # сюда будет слать iiko
HEALTH    = "/"                                   # корень для health-check

# ---------- хэндлеры ----------
async def health(_: web.Request) -> web.Response:
    """Health-check для Railway (200 OK)."""
    return web.json_response({"status": "alive"})

async def stoplist(request: web.Request) -> web.Response:
    """Принимаем JSON от iiko."""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "bad json"}, status=400)

    log.info("🚦  STOPLIST  %s  %s", datetime.now().isoformat(timespec="seconds"), data)
    # здесь можешь сохранять в БД, слать в TG и т.п.
    return web.json_response({"status": "ok"})

# ---------- запуск ----------
def main() -> None:
    app = web.Application()
    app.router.add_get (HEALTH   , health)
    app.router.add_post(STOP_PATH, stoplist)

    log.info("🚀  Server starting on port %s", PORT)
    log.info("    HEALTH:  %s", APP_URL + HEALTH)
    log.info("    STOPLIST: %s", APP_URL + STOP_PATH)

    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
