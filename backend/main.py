from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import get_current_user_info, router as auth_router  # ✅ 追加
from database import Base, engine, get_db
import models
from routers import reservations
from models import User as DBUser

app = FastAPI(
    title="GPU予約API",
    description="自然言語によるGPU予約とAIによる優先度判定のためのAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# 🔽 ルーター登録
app.include_router(auth_router, prefix="/auth")  # ← これ追加するだけ！
app.include_router(reservations.router, prefix="/api/reservations")

@app.get("/")
def read_root():
    return {"message": "APIはちゃんと動いてるよ！🎉"}

@app.get("/protected")
def protected_route(current_user: DBUser = Depends(get_current_user_info)):
    return {"message": f"{current_user.name}さん、ようこそ！🔐"}
