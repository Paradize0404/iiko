from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
from typing import List

log = logging.getLogger(__name__)
app = FastAPI()

class StopItem(BaseModel):
    name: str
    status: str

@app.get("/")
def root():
    return {"status": "alive"}

@app.post("/stoplist")
async def receive_stoplist(request: Request):
    raw_body = await request.body()

    try:
        decoded_body = raw_body.decode("utf-8")
        log.info("📩 RAW BODY (decoded): %s", decoded_body)
    except UnicodeDecodeError:
        log.warning("⚠️ Failed to decode raw body as UTF-8.")
        log.info("📩 RAW BODY (bytes): %s", raw_body)

    try:
        json_data = await request.json()
        log.info("📦 JSON RECEIVED: %s", json_data)

        # Поддержка как одного объекта, так и массива
        if isinstance(json_data, list):
            validated_items = [StopItem(**item) for item in json_data]
        elif isinstance(json_data, dict):
            validated_items = [StopItem(**json_data)]
        else:
            raise ValueError("Unsupported JSON structure")

        for item in validated_items:
            log.info("✅ STOP ITEM: %s", item.json())

        return {"status": "ok", "received": len(validated_items)}
    except Exception as e:
        log.error("❌ ERROR: %s", str(e))
        return {"status": "error", "message": str(e)}