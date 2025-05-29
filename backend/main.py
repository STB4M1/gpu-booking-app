from fastapi import FastAPI
from database import Base, engine
import models
from routers import reservations  # ← ルーター追加！

app = FastAPI()

Base.metadata.create_all(bind=engine)

# エンドポイント登録
app.include_router(reservations.router, prefix="/api/reservations")

@app.get("/")
def read_root():
    return {"message": "APIはちゃんと動いてるよ！🎉"}
