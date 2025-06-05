from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import get_current_user_info, router as auth_router  # ✅ 追加
from database import Base, engine, get_db
import models
from routers import reservations
from models import User as DBUser

def init_servers(db: Session):
    from models import Server  # 必ずここでimport（循環import防止）

    # ここで使用可能なサーバーを定義（必要に応じて増やしてOK）
    servers = [
        ("A100", 4),
        ("V100", 2),
        ("RTX3090", 1),
    ]

    for name, count in servers:
        if not db.query(Server).filter(Server.name == name).first():
            db.add(Server(name=name, gpu_count=count))

    db.commit()

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

# 🌟 サーバー初期化（重複追加されない）
with Session(bind=engine) as db:
    init_servers(db)


# 🔽 ルーター登録
app.include_router(auth_router, prefix="/auth")  # ← これ追加するだけ！
app.include_router(reservations.router, prefix="/api/reservations")

@app.get("/")
def read_root():
    return {"message": "APIはちゃんと動いてるよ！🎉"}

@app.get("/protected")
def protected_route(current_user: DBUser = Depends(get_current_user_info)):
    return {"message": f"{current_user.name}さん、ようこそ！🔐"}
