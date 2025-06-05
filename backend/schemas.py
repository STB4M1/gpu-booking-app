# 1. 標準ライブラリ 
from typing import Optional
from datetime import datetime
# 2. サードパーティライブラリ
from pydantic import BaseModel

# ---------- ユーザー関連 ----------
class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

# ---------- サーバー関連 ----------
class Server(BaseModel):
    id: int
    name: str
    gpu_count: int

    class Config:
        orm_mode = True

# ---------- 予約リクエスト（自然言語 or 構造化済） ----------
class ReservationCreate(BaseModel):
    server_id: int
    start_time: datetime
    end_time: datetime
    purpose: str

# ---------- 予約の応答（取得・一覧表示など） ----------
class Reservation(BaseModel):
    id: int
    user_id: int
    server_id: int
    start_time: datetime
    end_time: datetime
    purpose: str
    status: str
    priority_score: Optional[float] = None

    class Config:
        from_attributes = True

# ---------- 衝突ログ ----------
class ConflictLog(BaseModel):
    id: int
    reservation_1: int
    reservation_2: int
    resolved: bool

    class Config:
        orm_mode = True

# ★ 追加：自然文の入力用スキーマ
class NaturalTextRequest(BaseModel):
    text: str

# ★ 追加：自然文を構造化したレスポンス
class StructuredReservationResponse(BaseModel):
    start_time: str
    end_time: str
    purpose: str
    priority_score: float

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    server_id: int
    start_time: datetime
    end_time: datetime
    purpose: str
    status: str
    priority_score: Optional[float] = None
    received_text: Optional[str] = None  # 👈 ここを Optional にする！

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str