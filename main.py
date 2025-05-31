from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
from typing import List

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)
app = FastAPI()

class StopItem(BaseModel):
    productId: str
    productName: str
    available: bool
    timestamp: str

@app.get("/")
def root():
    return {"status": "alive"}

@app.post("/stoplist")
async def receive_stoplist(request: Request):
    raw_body = await request.body()

    try:
        decoded = raw_body.decode("utf-8")
        log.info("📩 RAW BODY (decoded): %s", decoded)
    except Exception as e:
        log.warning("⚠️ Cannot decode body as UTF-8: %s", str(e))
        log.info("📩 RAW BODY (bytes): %s", raw_body)

    try:
        json_data = await request.json()
        log.info("📦 JSON RECEIVED: %s", json_data)

        if isinstance(json_data, list):
            items_raw = json_data
        elif isinstance(json_data, dict) and "stopListItems" in json_data:
            items_raw = json_data["stopListItems"]
        else:
            raise ValueError("Неподдерживаемая структура JSON")

        # 🔍 Выводим объекты из stopListItems как есть — без валидации
        for item in items_raw:
            log.info("🔍 ОБЪЕКТ ВНУТРИ: %s", item)

        return {"status": "ok", "received": len(items_raw)}
    except Exception as e:
        log.error("❌ ERROR while parsing or inspecting: %s", str(e))
        return {"status": "error", "message": str(e)}