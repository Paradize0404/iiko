from fastapi import FastAPI
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
async def receive_stoplist(item: StopItem):
    log.info("🚦 STOPLIST %s", item.json())
    return {"status": "ok"}