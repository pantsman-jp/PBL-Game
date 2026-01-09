"""
システム管理 | src/core/system.py
セーブ/ロードおよびBGM制御を提供
"""

import os
import pygame
from src.utils import save_json, load_json, SAVEFILE, resource_path


class System:
    """
    ゲームの進行フラグ、セーブデータ、音響再生を統括するクラス
    """

    def __init__(self, app):
        self.app = app
        self.savefile = SAVEFILE

        # ゲーム進行フラグの初期化
        self.flags = {
            "intro_done": False,
            "item_cfrp": False,
            "item_engine": False,
            "item_cpu": False,
            "rocket_assembled": False,
        }

    # --- フラグ操作 ---

    def set_flag(self, key, value=True):
        """フラグの状態を設定"""
        self.flags[key] = value

    def get_flag(self, key):
        """フラグの状態を取得（存在しない場合はFalse）"""
        return self.flags.get(key, False)

    # --- 目的（Objective）管理 ---

    def get_current_objective(self):
        """
        現在のフラグ状態に基づいて、画面上部に表示する目標テキストを生成する
        """
        # 1. 導入フェーズ
        if not self.flags["intro_done"]:
            return "目標：案内人に話しかけて指示を仰げ"

        # 2. 部品収集フェーズ
        # 各部品のフラグと対応するメッセージを定義
        parts_info = [
            ("item_cfrp", "複合材料研究室へ向かい、CFRPを入手せよ"),
            ("item_engine", "実習工場へ向かい、エンジンを入手せよ"),
            ("item_cpu", "情報工学棟へ向かい、制御基板を入手せよ"),
        ]

        for flag_key, message in parts_info:
            if not self.flags[flag_key]:
                return f"目標：{message}"

        # 3. 最終フェーズ
        if not self.flags["rocket_assembled"]:
            return "目標：部品は揃った。ロケットを組み立てろ！"

        return "目標：種子島へ向かい、ロケットを打ち上げろ！"

    # --- データ永続化（セーブ・ロード） ---

    def save(self):
        """現在のプレイヤー座標、所持アイテム、フラグを保存"""
        data = {
            "x": self.app.x,
            "y": self.app.y,
            "items": self.app.items,
            "flags": self.flags,
        }

        try:
            save_json(self.savefile, data)
            print(f"System: Successfully saved to {self.savefile}")
        except Exception as e:
            print(f"System: Save Error! - {e}")

    def load(self):
        """保存されたデータを読み込み、アプリの状態を復元"""
        data = load_json(self.savefile)
        if not data:
            return False

        try:
            self.app.x = data.get("x", self.app.x)
            self.app.y = data.get("y", self.app.y)
            self.app.items = data.get("items", [])
            self.flags = data.get("flags", self.flags)

            print(f"System: Successfully loaded from {self.savefile}")
            return True
        except Exception as e:
            print(f"System: Load Error! - {e}")
            return False

    # --- BGM制御 ---
    def play_bgm(self, path):
        if not pygame.mixer.get_init() or not path:
            return

        full_path = resource_path(path)
        print("DEBUG: play_bgm full_path =", full_path)
        print("DEBUG: play_bgm called for", full_path)
        if not os.path.isfile(full_path):
            print("BGM not found:", full_path)
            return

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"System: BGM Playback Error - {e}")

    def stop_bgm(self):
        # ミキサーが使用可能かチェック
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
