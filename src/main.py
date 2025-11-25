"""
メインエントリポイント | src/main.py

ゲームの起動処理は app.py に任せる
"""

from src.app import App
import traceback

if __name__ == "__main__":
    try:
        App().run()
    except Exception:
        traceback.print_exc()
        raise Exception("Something wrong")
