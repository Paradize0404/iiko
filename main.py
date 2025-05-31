from fastapi import FastAPI, Request
import os
import uvicorn


app = FastAPI()

@app.post("/stoplist")
async def receive_stoplist(request: Request):
    data = await request.json()
    print("🔔 Получен POST-запрос от iiko:")
    print(data)
    return {"status": "ok"}




# 👇 Добавь вот это в самый конец
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)