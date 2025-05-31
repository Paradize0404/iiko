import os
import logging
from typing import List
from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI()

class StopItem(BaseModel):
    productId: str
    productName: str
    available: bool
    timestamp: str

# 🚀 Запрос в iiko при старте приложения
@app.on_event("startup")
async def on_startup():
    org_id = os.getenv("IIKO_ORG_ID")
    if not org_id:
        log.warning("❗️ IIKO_ORG_ID не задан — запрос в iiko при запуске не выполнен.")
        return
    try:
        log.info("🟢 Старт сервера. Получаю стоп-лист для организации %s", org_id)
        stoplist = await fetch_stoplist_from_iiko(org_id)
        log.info("📋 СТОП-ЛИСТ ПРИ СТАРТЕ: %s", stoplist)
    except Exception as e:
        log.error("❌ Ошибка при получении стоп-листа на старте: %s", str(e))

# 🔄 Основной эндпоинт для webhook от iiko
@app.post("/stoplist")
async def receive_stoplist(request: Request):
    try:
        json_data = await request.json()
        log.info("📦 Вебхук от iiko: %s", json_data)

        if isinstance(json_data, list):
            event = json_data[0]
        else:
            raise ValueError("Ожидался список в корне JSON")

        org_id = event.get("organizationId")
        if not org_id:
            raise ValueError("Нет organizationId в webhook")

        stoplist = await fetch_stoplist_from_iiko(org_id)
        log.info("📥 ОБНОВЛЁННЫЙ СТОП-ЛИСТ: %s", stoplist)

        return {"status": "ok", "items": len(stoplist)}
    except Exception as e:
        log.error("❌ Ошибка в обработке вебхука: %s", str(e))
        return {"status": "error", "message": str(e)}

# 🔌 Запрос в iiko Cloud
async def fetch_stoplist_from_iiko(organization_id: str):
    api_key = os.getenv("IIKO_API_KEY")
    if not api_key:
        raise RuntimeError("IIKO_API_KEY не задан в переменных окружения")

    log.info("🔐 Текущий IIKO_API_KEY (обрезан): %s...", api_key[:6])

    url = "https://api-ru.iiko.services/api/1/stopLists"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {"organizationId": organization_id}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
