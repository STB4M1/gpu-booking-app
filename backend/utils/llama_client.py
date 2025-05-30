import os
import requests
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数から URL を取得（デフォルトURLは空にしておく）
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "").strip()

if not LLAMA_API_URL:
    raise RuntimeError("❌ LLAMA_API_URL が .env に設定されていません")

def analyze_text_with_llama(text: str) -> dict:
    try:
        response = requests.post(LLAMA_API_URL, json={"text": text}, verify=False)  # verify=Falseは開発用
        response.raise_for_status()
        result = response.json()
        print("🧠 LLaMA構造化結果:", result)  # ログ出力（任意）
        return result
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"LLaMA構造化API呼び出し失敗: {e}")
