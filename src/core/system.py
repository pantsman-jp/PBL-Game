"""
システム管理 | src/core/system.py
セーブ/ロードおよびBGM制御を提供
"""

from src.utils import save_json, load_json, SAVEFILE, resource_path
import pygame
import os


class System:
    def __init__(self, app):
        self.app = app
        self.savefile = SAVEFILE
        # フラグ初期化
        self.flags = {
            "intro_done": False,
            "item_cfrp": False,
            "item_engine": False,
            "item_cpu": False,
            "rocket_assembled": False,
        }

    def set_flag(self, key, value=True):
        self.flags[key] = value

    def get_flag(self, key):
        return self.flags.get(key, False)

    def get_current_objective(self):
        """現在のフラグ状態に基づいて目標テキストを返す"""
        if not self.flags["intro_done"]:
            return "目標：案内人に話しかけて指示を仰げ"

        # 部品収集フェーズ
        missing_parts = []
        if not self.flags["item_cfrp"]:
            missing_parts.append("CFRP")
        if not self.flags["item_engine"]:
            missing_parts.append("エンジン")
        if not self.flags["item_cpu"]:
            missing_parts.append("制御基板")

        if missing_parts:
            # 優先度の高いものを表示、あるいは「○○と○○を探せ」とする
            # ここではシンプルに最初の1つを表示する
            target = missing_parts[0]
            if target == "CFRP":
                return "目標：複合材料研究室へ向かい、CFRPを入手せよ"
            elif target == "エンジン":
                return "目標：実習工場へ向かい、エンジンを入手せよ"
            elif target == "制御基板":
                return "目標：情報工学棟へ向かい、制御基板を入手せよ"

        if not self.flags["rocket_assembled"]:
            return "目標：部品は揃った。ロケットを組み立てろ！"

        return "目標：種子島へ向かい、ロケットを打ち上げろ！"

    def save(self):
        data = {
            "x": self.app.x,
            "y": self.app.y,
            "items": self.app.items,
            "flags": self.flags,
        }
        save_json(self.savefile, data)
        print("Saved:", self.savefile)

    def load(self):
        data = load_json(self.savefile)
        if data:
            self.app.x = data.get("x", self.app.x)
            self.app.y = data.get("y", self.app.y)
            self.app.items = data.get("items", [])
            self.flags = data.get("flags", self.flags)
            print("Loaded save:", self.savefile)
            return True
        return False

    def play_bgm(self, path):
        if path is None:
            return
        path = resource_path(path)
        if not os.path.isfile(path):
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("BGM再生エラー:", e)

    def stop_bgm(self):
        pygame.mixer.music.stop()
