from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging

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
    log.info("📩 RAW BODY: %s", raw_body.decode("utf-8"))

    try:
        item = await request.json()
        validated = StopItem(**item)
        log.info("✅ VALIDATED ITEM: %s", validated.json())
        return {"status": "ok"}
    except Exception as e:
        log.error("❌ ERROR: %s", str(e))
        return {"status": "error", "message": str(e)}