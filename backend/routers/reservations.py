from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from database import get_db
import models, schemas
from schemas import NaturalTextRequest, ReservationCreate

router = APIRouter()

# === 自然文 → 構造化 → 優先度判定 → DB登録 ===
@router.post("/natural", response_model=schemas.Reservation)
def create_reservation_from_natural(
    request: NaturalTextRequest,
    db: Session = Depends(get_db)
):
    # --- 仮構造化（後でLLaMA連携予定） ---
    structured = {
        "start_time": "2025-06-03T13:00:00",
        "end_time": "2025-06-03T17:00:00",
        "purpose": "ゼミの検証実験",
        "priority_score": 0.85
    }

    # --- 日時の形式変換 ---
    try:
        start_dt = datetime.fromisoformat(structured["start_time"])
        end_dt = datetime.fromisoformat(structured["end_time"])
    except Exception:
        raise HTTPException(status_code=400, detail="日時フォーマットが不正です")

    # --- ReservationCreate でバリデーション ---
    reservation_in = ReservationCreate(
        server_id=1,
        start_time=start_dt,
        end_time=end_dt,
        purpose=structured["purpose"]
    )

    # --- 重複予約検出 ---
    overlapping = db.query(models.Reservation).filter(
        models.Reservation.server_id == reservation_in.server_id,
        models.Reservation.end_time > reservation_in.start_time,
        models.Reservation.start_time < reservation_in.end_time,
        models.Reservation.status.in_(["approved", "pending"])
    ).all()

    # --- 優先度比較 ---
    is_high_priority = True
    for existing in overlapping:
        if existing.priority_score is not None and existing.priority_score >= structured["priority_score"]:
            is_high_priority = False
            break

    # --- ステータス決定 ---
    status = "approved" if is_high_priority else "pending_conflict"

    # --- 予約登録 ---
    reservation = models.Reservation(
        user_id=1,  # 仮ユーザー
        server_id=reservation_in.server_id,
        start_time=reservation_in.start_time,
        end_time=reservation_in.end_time,
        purpose=reservation_in.purpose,
        priority_score=structured["priority_score"],
        status=status
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation

# === 保留中予約一覧取得 ===
@router.get("/conflicts", response_model=List[schemas.Reservation])
def get_pending_conflicts(db: Session = Depends(get_db)):
    reservations = db.query(models.Reservation).filter(
        models.Reservation.user_id == 1,
        models.Reservation.status == "pending_conflict"
    ).all()
    return reservations

@router.patch("/{reservation_id}/confirm-cancel", response_model=schemas.Reservation)
def confirm_cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db)
):
    # 対象の保留中予約を取得（user_id=1 仮）
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id,
        models.Reservation.user_id == 1,
        models.Reservation.status == "pending_conflict"
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="対象予約が見つかりません")

    # ステータスを「rejected」に更新
    reservation.status = "rejected"
    db.commit()
    db.refresh(reservation)

    return reservation


# --- 自分の予約一覧を取得するエンドポイント ---
@router.get("/me", response_model=List[schemas.Reservation])
def get_my_reservations(db: Session = Depends(get_db)):
    return db.query(models.Reservation).filter(models.Reservation.user_id == 1).all()

# --- 自分の予約をキャンセルするエンドポイント ---
@router.patch("/{reservation_id}/cancel", response_model=schemas.Reservation)
def cancel_my_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id,
        models.Reservation.user_id == 1  # 仮ユーザー
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="予約が見つかりません")

    reservation.status = "rejected"
    db.commit()
    db.refresh(reservation)
    return reservation
