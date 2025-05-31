from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
from typing import List

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
        log.info("📦 FULL JSON RECEIVED: %s", json_data)

        # Достаём список блюд из объекта iiko
        items_raw = json_data.get("stopListItems", [])
        if not isinstance(items_raw, list):
            raise ValueError("stopListItems must be a list")

        # Валидация каждого элемента
        items = [StopItem(**item) for item in items_raw]

        for item in items:
            log.info("✅ STOP ITEM: %s — %s (%s)", item.productName, "❌ НЕТ" if not item.available else "✅ ЕСТЬ", item.timestamp)

        return {"status": "ok", "received": len(items)}
    except Exception as e:
        log.error("❌ ERROR while parsing or validating: %s", str(e))
        return {"status": "error", "message": str(e)}