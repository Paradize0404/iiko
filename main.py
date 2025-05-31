from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/stoplist")
async def receive_stoplist(request: Request):
    data = await request.json()
    print("🔔 Получен POST-запрос от iiko:")
    print(data)
    return {"status": "ok"}