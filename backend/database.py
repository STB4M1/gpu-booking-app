# 2. サードパーティライブラリ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLiteファイルのパスを指定（ローカルファイルとして保存される）
SQLALCHEMY_DATABASE_URL = "sqlite:///./gpu_reservation.db"

# SQLite用のエンジン作成（check_same_threadはSQLite特有の設定）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# セッションを作るためのクラス
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 全モデルで使い回す「ベースクラス」
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
