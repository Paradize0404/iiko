import os, requests
from fastapi import FastAPI

API_LOGIN = os.getenv("IIKO_API_LOGIN")               # 287a6693-…  (HEX)
BASE      = "https://api-ru.iiko.services"

app = FastAPI()

def get_access_token() -> str:
    r = requests.post(f"{BASE}/api/1/access_token",
                      json={"apiLogin": API_LOGIN},
                      timeout=15)
    r.raise_for_status()
    token = r.json()["token"]
    print("✅ access_token получен")
    return token

def fetch_orgs(token: str):
    r = requests.post(f"{BASE}/api/1/organizations",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"},
                      json={}, timeout=15)
    r.raise_for_status()
    orgs = r.json()["organizations"]
    print("📋 Организации:")
    for o in orgs:
        print(f"- {o['name']} ({o['id']})")
    return orgs

@app.on_event("startup")
def startup_task():
    token = get_access_token()
    fetch_orgs(token)

@app.get("/")
def root():
    return {"status": "OK"}