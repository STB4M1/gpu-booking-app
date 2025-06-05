# 1. 標準ライブラリ 
from datetime import datetime
from typing import List
# 2. サードパーティライブラリ
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
# 3. ローカルモジュール（自作モジュール）
from database import get_db
import models
import schemas
from schemas import NaturalTextRequest, ReservationCreate
from schemas import ReservationResponse
from utils.llama_client import analyze_text_with_llama
from fastapi import Depends
from database import get_db  # DB接続用
from models import Reservation  # 予約テーブル
from models import User as UserModel  # ← これが「DBのUser」やから必須！
from auth import get_current_user, User  # ← これは認証用User（Pydantic）

router = APIRouter()

# === 自然文 → 構造化 → 優先度判定 → DB登録 ===
@router.post("/natural", response_model=schemas.ReservationResponse)
def create_reservation_from_natural(
    request: NaturalTextRequest,
    db: Session = Depends(get_db)
):
    try:
        # 1. Colabから自然文を構造化
        structured = analyze_text_with_llama(request.text)

        # 2. 必須キーの存在チェック
        required_keys = {"start_time", "end_time", "purpose", "priority_score"}
        if not required_keys.issubset(structured):
            raise HTTPException(status_code=422, detail="構造化結果に必要なキーが足りません")

        # 3. ISO8601形式として日時をパース（Colabが "T08:00:00" を返す前提）
        start_dt = datetime.fromisoformat(structured["start_time"])
        end_dt = datetime.fromisoformat(structured["end_time"])

        # 4. バリデーション付き入力データ生成
        reservation_in = ReservationCreate(
            server_id=1,
            start_time=start_dt,
            end_time=end_dt,
            purpose=structured["purpose"]
        )

        # 5. 重複予約の取得
        overlapping = db.query(models.Reservation).filter(
            models.Reservation.server_id == reservation_in.server_id,
            models.Reservation.end_time > reservation_in.start_time,
            models.Reservation.start_time < reservation_in.end_time,
            models.Reservation.status.in_(["approved", "pending"])
        ).all()

        # 6. 優先度比較
        is_high_priority = True
        for existing in overlapping:
            if existing.priority_score is not None and existing.priority_score >= structured["priority_score"]:
                is_high_priority = False
                break

        # 7. ステータス決定 & 他予約の更新
        status = "approved" if is_high_priority else "pending_conflict"
        if is_high_priority:
            for existing in overlapping:
                existing.status = "pending_conflict"
                db.add(existing)

        # 8. DBに新しい予約を追加
        reservation = models.Reservation(
            user_id=1,  # 仮ユーザー（認証導入時に差し替え可）
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

        # 9. レスポンス生成（予約情報＋自然文）
        response_obj = schemas.ReservationResponse.from_orm(reservation)
        response_obj.received_text = structured.get("received_text", request.text)

        print("✅ レスポンス内容:", response_obj)
        return response_obj

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

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
# @router.get("/me", response_model=List[schemas.Reservation])
# def get_my_reservations(db: Session = Depends(get_db)):
#     return db.query(models.Reservation).filter(models.Reservation.user_id == 1).all()

# @router.get("/me")
# def get_my_reservations(current_user: User = Depends(get_current_user)):
#     return {
#         "user": current_user.username,
#         "reservations": []  # 👈 空リストをちゃんと返す！
#     }
@router.get("/me")
def get_my_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. ユーザーのDBオブジェクトを取得
    user_obj = db.query(UserModel).filter(UserModel.username == current_user.username).first()

    # 2. そのユーザーに紐づく予約を取得
    reservations = db.query(Reservation).filter(Reservation.user == user_obj).all()

    return {
        "user": current_user.username,
        "reservations": reservations
    }

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

@router.get("/test-colab")
def test_colab_connection():
    import requests

    colab_url = "https://fbe7-35-231-243-8.ngrok-free.app/analyze"  # ← Colabの表示したngrok URLに置き換えて！
    try:
        res = requests.post(colab_url, json={"text": "WSLのFastAPIからColabの通信できてくれーーー！！！"})
        return {
            "status": res.status_code,
            "response": res.json()
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/test-flutter")
def receive_from_flutter(request: NaturalTextRequest):
    print("📱 Flutterから受信:", request.text)
    return {
        "message": "FastAPIはちゃんとFlutterから受け取ったで！🎉",
        "received_text": request.text
    }