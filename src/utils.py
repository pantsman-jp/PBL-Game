"""
汎用ユーティリティ | src/utils.py
キー状態取得、JSON save/load、リソースパス解決
"""

import pygame
import json
import sys
from pathlib import Path

# --- 定数定義 ---
SAVEFILE = "save.json"
DIALOGUES = "assets/dialogues/dialogues.json"


class KeyTracker:
    """
    キー入力の「押し下げられた瞬間」のみを検出するクラス。
    長押しによる連続入力を防ぎ、クイズの選択やテキスト送りを快適にします。
    """

    # 追跡対象のキーマップを定義
    TRACKED_KEYS = {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "z": pygame.K_z,
        "q": pygame.K_q,
        "s": pygame.K_s,
        "i": pygame.K_i,
        "m": pygame.K_m,
        "0": pygame.K_0,
        "1": pygame.K_1,
        "2": pygame.K_2,
        "3": pygame.K_3,
        "4": pygame.K_4,
        "5": pygame.K_5,
        "6": pygame.K_6,
        "7": pygame.K_7,
        "8": pygame.K_8,
        "9": pygame.K_9,
        "backspace": pygame.K_BACKSPACE,
        ".": pygame.K_PERIOD,
    }

    def __init__(self):
        # 1フレーム前のキー状態を保持
        self.prev_state = pygame.key.get_pressed()

    def update(self):
        """
        現在のキー状態を確認し、前回押されておらず、今回押されているキーを辞書で返します。
        """
        current_state = pygame.key.get_pressed()
        triggered = {}

        for name, key_code in self.TRACKED_KEYS.items():
            # 「今押されている」かつ「前回は押されていなかった」場合のみTrue
            triggered[name] = current_state[key_code] and not self.prev_state[key_code]

        self.prev_state = current_state
        return triggered


def save_json(path_str, data):
    """
    データをJSON形式でファイルに保存します。
    ディレクトリが存在しない場合は自動的に作成します。
    """
    try:
        path = Path(path_str)
        # 親ディレクトリが存在しない場合は作成
        path.parent.mkdir(parents=True, exist_ok=True)

        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        path.write_text(json_content, encoding="utf-8")
    except Exception as e:
        print(f"utils.save_json: エラーが発生しました - {e}")


def load_json(path_str):
    """
    JSONファイルを読み込み、辞書形式で返します。
    ファイルが存在しない、または破損している場合は None を返します。
    """
    path = Path(path_str)
    if not path.exists():
        return None

    try:
        content = path.read_text(encoding="utf-8")
        return json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"utils.load_json: 読み込みエラー - {e}")
        return None


def resource_path(relative_path):
    """
    PyInstallerによるEXE化後と開発環境の両方で、正しいリソースパスを返します。
    """
    try:
        # PyInstallerが一時的に解凍するフォルダパスを取得
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # 開発環境（実行ファイルのあるディレクトリ）を基準にする
        base_path = Path(__file__).resolve().parent.parent

    # 相対パスを絶対パスに結合して返す
    return str(base_path / relative_path)
