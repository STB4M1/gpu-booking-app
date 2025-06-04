# ✅ 一般的な順番：
# 1. 標準ライブラリ
# 2. サードパーティライブラリ
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 3. 自作モジュール
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
    allow_origins=["*"],  # すべてのオリジンからのアクセスを許可（開発中はOK）
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

Base.metadata.create_all(bind=engine)

# エンドポイント登録
app.include_router(reservations.router, prefix="/api/reservations")

@app.get("/")
def read_root():
    return {"message": "APIはちゃんと動いてるよ！🎉"}
