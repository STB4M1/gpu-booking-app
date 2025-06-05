from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 仮のユーザーDB（実際はDBと連携してもOK）
fake_users_db = {
    "mitsu": {
        "username": "mitsu",
        "full_name": "Mitsu GPU User",
        "password": "gpu123",  # 本当はハッシュ化するべき
    }
}

class User(BaseModel):
    username: str
    full_name: str

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # トークン＝ユーザー名として使うシンプル仕様
    user_data = fake_users_db.get(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return User(**user_data)
