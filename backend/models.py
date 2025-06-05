# 2. サードパーティライブラリ
from sqlalchemy import (
    Column, Integer, String, Boolean,
    ForeignKey, DateTime, Float, Text, Enum
)
from sqlalchemy.orm import relationship
# 3. ローカルモジュール（自作モジュール）
from database import Base  # ※ database.pyでBaseを定義します（次ステップで）
import models

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # ← 🔑 追加！
    is_admin = Column(Boolean, default=False)

    reservations = relationship("Reservation", back_populates="user")


# サーバーテーブル
class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    gpu_count = Column(Integer)

    reservations = relationship("Reservation", back_populates="server")

# 予約テーブル
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    server_id = Column(Integer, ForeignKey("servers.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    purpose = Column(Text)
    status = Column(
    Enum(
        "confirmed",
        "pending",
        "rejected",
        "waiting",
        "pending_conflict",
        "approved", 
        name="reservation_status"
    ),
    default="pending"
)

    priority_score = Column(Float)

    user = relationship("User", back_populates="reservations")
    server = relationship("Server", back_populates="reservations")

# 衝突ログテーブル
class ConflictLog(Base):
    __tablename__ = "conflict_logs"

    id = Column(Integer, primary_key=True, index=True)
    reservation_1 = Column(Integer, ForeignKey("reservations.id"))
    reservation_2 = Column(Integer, ForeignKey("reservations.id"))
    resolved = Column(Boolean, default=False)
