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

    def save(self):
        data = {"x": self.app.x, "y": self.app.y, "items": self.app.items}
        save_json(self.savefile, data)
        print("Saved:", self.savefile)

    def load(self):
        data = load_json(self.savefile)
        if data:
            self.app.x = data.get("x", self.app.x)
            self.app.y = data.get("y", self.app.y)
            self.app.items = data.get("items", [])
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
