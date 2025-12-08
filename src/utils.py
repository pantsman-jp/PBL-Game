"""
汎用ユーティリティ | utils.py
キー状態取得、JSON save/load
"""

import pygame
import json
import os
import sys
from pathlib import Path

SAVEFILE = "save.json"
DIALOGUES = "assets/dialogues/dialogues.json"


class KeyTracker:
    """押下タイミングを検出するキー入力管理"""

    def __init__(self):
        self.prev = pygame.key.get_pressed()

    def update(self):
        cur = pygame.key.get_pressed()
        pressed_once = {}
        for [name, key] in {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "z": pygame.K_z,
            "q": pygame.K_q,
            "s": pygame.K_s,
        }.items():
            pressed_once[name] = cur[key] and not self.prev[key]
        self.prev = cur
        return pressed_once


def save_json(path, data):
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_json(path):
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
