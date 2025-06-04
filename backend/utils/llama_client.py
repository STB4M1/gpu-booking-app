import os
import requests
import time
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数から LLaMA構造化APIのURLを取得
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "").strip()

if not LLAMA_API_URL:
    raise RuntimeError("❌ LLAMA_API_URL が .env に設定されていません")

def analyze_text_with_llama(text: str, retries: int = 3, delay: float = 1.5) -> dict:
    """
    自然文を Colab の LLaMA構造化API に送信して、構造化JSONを取得する。
    
    Parameters:
        text (str): 入力する自然文
        retries (int): 通信失敗時の再試行回数
        delay (float): 再試行間の待機時間（秒）

    Returns:
        dict: 構造化された辞書形式のレスポンス
    """
    for attempt in range(1, retries + 1):
        try:
            print(f"📤 Colabへ送信（試行{attempt}/{retries}）: {LLAMA_API_URL}")
            print(f"📝 入力テキスト: {text}")

            response = requests.post(
                LLAMA_API_URL,
                headers={"Content-Type": "application/json"},
                json={"text": text},
                verify=False
            )

            print(f"📡 ステータスコード: {response.status_code}")
            print("📩 応答本文:", response.text)

            response.raise_for_status()
            result = response.json()
            print("🧠 構造化結果:", result)
            return result

        except requests.exceptions.RequestException as e:
            print(f"⚠️ 通信失敗（試行{attempt}）: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                raise RuntimeError(f"❌ LLaMA構造化API呼び出し失敗（{retries}回試行後）: {e}")

