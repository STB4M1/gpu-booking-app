from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Alembic の設定オブジェクト（.iniファイルを読み込む）
config = context.config

# ロギングの初期化
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ==========================================
# ✅ 以下を追加：Base.metadata を読み込むための設定
# backend/database.py を import するためにパスを通す
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base  # ← database.py にある Base を import

# autogenerate のために metadata を設定
target_metadata = Base.metadata
# ==========================================

# オフラインマイグレーション関数
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# オンラインマイグレーション関数
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

# 実行モードに応じて処理を分岐
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
