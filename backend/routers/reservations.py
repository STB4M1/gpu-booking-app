# 1. 標準ライブラリ
from datetime import datetime
from typing import List
# 2. サードパーティライブラリ
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
# 3. ローカルモジュール（自作モジュール）
from database import get_db
from models import Reservation, User as UserModel
from schemas import (
    NaturalTextRequest,
    ReservationCreate,
    ReservationResponse,
    UserCreate,
    User,  # 認証されたユーザー情報のスキーマ（Pydantic）
)
from auth import get_current_user_info as get_current_user  # 認証関数（auth.pyにある想定）
from utils.llama_client import analyze_text_with_llama
import schemas
import models

router = APIRouter()

# === 自然文 → 構造化 → 優先度判定 → DB登録 ===
@router.post("/natural", response_model=schemas.ReservationResponse)
def create_reservation_from_natural(
    request: NaturalTextRequest,
    current_user: User = Depends(get_current_user),
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

        # サーバー名からIDを取得
        server_name = structured.get("server_name")
        if not server_name:
            raise HTTPException(status_code=422, detail="構造化結果にserver_nameが含まれていません")

        server = db.query(models.Server).filter(models.Server.name == server_name).first()
        if not server:
            raise HTTPException(status_code=404, detail=f"サーバー '{server_name}' が見つかりません")

        # 4. バリデーション付き入力データ生成
        reservation_in = ReservationCreate(
            server_id=server.id,
            start_time=start_dt,
            end_time=end_dt,
            purpose=structured["purpose"]
        )

        # 5. 重複予約の取得
        overlapping = db.query(models.Reservation).filter(
            models.Reservation.server_id == reservation_in.server_id,
            models.Reservation.end_time > reservation_in.start_time,
            models.Reservation.start_time < reservation_in.end_time,
            models.Reservation.status == "approved"
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
            user_id=current_user.id,
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
        response_obj.server_name = reservation.server.name
        print("✅ レスポンス内容:", response_obj)
        return response_obj

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

# === 保留中予約一覧取得 ===
@router.get("/conflicts", response_model=List[schemas.ReservationResponse])
def get_conflicting_reservations(db: Session = Depends(get_db)):
    reservations = db.query(Reservation).filter(Reservation.status == "pending_conflict").all()

    result = []
    for r in reservations:
        res_dict = schemas.ReservationResponse.from_orm(r).dict()
        res_dict["server_name"] = r.server.name if r.server else None
        result.append(schemas.ReservationResponse(**res_dict))
    return result

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
@router.get("/me", response_model=List[schemas.ReservationResponse])
def get_my_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_obj = db.query(UserModel).filter(UserModel.username == current_user.username).first()
    reservations = db.query(Reservation).filter(Reservation.user == user_obj).all()

    # 🧠 ← ここで server_name を含めて整形
    response = []
    for r in reservations:
        response.append(schemas.ReservationResponse(
            id=r.id,
            start_time=r.start_time,
            end_time=r.end_time,
            purpose=r.purpose,
            priority_score=r.priority_score or 0.0,
            status=r.status,
            server_name=r.server.name if r.server else "(未設定)",
            received_text=None  # 任意
        ))
    return response

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

@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    if db.query(UserModel).filter(UserModel.username == user.username).first():
        raise HTTPException(status_code=400, detail="ユーザー名は既に存在します")

    hashed_pw = pwd_context.hash(user.password)

    new_user = UserModel(
        username=user.username,
        hashed_password=hashed_pw,
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "登録成功"}

@router.delete("/{reservation_id}", response_model=schemas.ReservationResponse)
def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="予約が見つかりません")

    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="自分の予約しかキャンセルできません")

    reservation.status = "cancelled"
    db.commit()
    db.refresh(reservation)
    return reservation

@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="ユーザー名またはパスワードが違います")

    return {"access_token": user.username, "token_type": "bearer"}


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