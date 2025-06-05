from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from auth import get_current_user, fake_users_db, User  # 👈 追加

from database import Base, engine
import models
from routers import reservations

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
app.include_router(reservations.router, prefix="/api/reservations")

@app.get("/")
def read_root():
    return {"message": "APIはちゃんと動いてるよ！🎉"}

# 👇 トークン発行（ログイン）
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user["username"], "token_type": "bearer"}

# 👇 テスト用の保護ルート（認証必要）
@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"{current_user.full_name}さん、ようこそ！🔐"}
