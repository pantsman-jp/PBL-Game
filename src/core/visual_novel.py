"""
ビジュアルノベル管理 | src/core/visual_novel.py
立ち絵、背景、テキストウィンドウによる会話イベントを制御
"""

import pygame
import os
from src.utils import resource_path, load_json
from src.ui import draw_window

# --- レイアウト定数 ---
VN_SCREEN_W = 900
VN_SCREEN_H = 700
CHAR_POS = (VN_SCREEN_W // 2, 600)  # 立ち絵の配置（中央下部）
TEXT_BOX_RECT = (50, 500, 800, 150)


class VisualNovel:
    """
    ノベルパート（会話イベント）の進行と描画を管理するクラス
    """

    def __init__(self, app):
        self.app = app
        self.base_dir = resource_path("assets")

        # 状態管理
        self.active = False
        self.script = []
        self.index = 0

        # リソース管理
        self.bg_image = None
        self.char_image = None
        self._image_cache = {}  # 重複ロード防止用のキャッシュ

        # データロード
        scripts_path = os.path.join(self.base_dir, "data", "novel_scripts.json")
        self.scripts_data = load_json(scripts_path) or {}
        self.font = app.font

    def start(self, script_id):
        """指定されたIDのシナリオを開始する"""
        if script_id not in self.scripts_data:
            print(f"VisualNovel: Script ID '{script_id}' not found.")
            self.end_scene()
            return

        self.script = self.scripts_data[script_id]
        self.index = 0
        self.active = True
        self._load_current_scene()

    def _get_cached_image(self, name, alpha=False):
        """画像をロードし、キャッシュから返す。名前が 'none' の場合は None を返す。"""
        if not name or name.lower() == "none":
            return None

        if name in self._image_cache:
            return self._image_cache[name]

        path = os.path.join(self.base_dir, "img", name)
        if not os.path.isfile(path):
            print(f"VisualNovel: Resource not found - {path}")
            return None

        # ロード処理
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()

        # 背景の場合は画面サイズにリサイズ
        if not alpha:
            img = pygame.transform.scale(img, (VN_SCREEN_W, VN_SCREEN_H))

        self._image_cache[name] = img
        return img

    def _load_current_scene(self):
        """現在のインデックスに基づき背景と立ち絵を更新する"""
        if self.index >= len(self.script):
            self.end_scene()
            return

        data = self.script[self.index]

        # 背景の更新（指定がある場合のみ）
        bg_name = data.get("bg")
        if bg_name:
            path = resource_path(os.path.join(self.base_dir, "img", bg_name))
            if os.path.isfile(path):
                self.bg_image = pygame.image.load(path).convert()
                # 画面サイズに合わせてスケール（必要に応じて）
                self.bg_image = pygame.transform.scale(self.bg_image, (900, 700))

        # 立ち絵の更新（指定がある場合のみ、"none" で消去）
        char_name = data.get("char")
        if char_name:
            if char_name.lower() == "none":
                self.char_image = None
            else:
                path = resource_path(os.path.join(self.base_dir, "img", char_name))
                if os.path.isfile(path):
                    img = pygame.image.load(path).convert_alpha()
                    # 立ち絵のサイズ調整（例: 高さ400pxに合わせるなど）
                    # ここではそのまま表示
                    self.char_image = img

    def update(self, events):
        """入力イベントに応じたページ送り処理"""
        if not self.active:
            return

        for ev in events:
            # クリックまたはスペースキーで進行
            is_click = ev.type == pygame.MOUSEBUTTONDOWN
            is_space = ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE

            if is_click or is_space:
                self.index += 1
                self._load_current_scene()

    def draw(self, screen):
        """背景 -> 立ち絵 -> テキストボックスの順に描画"""
        if not self.active:
            return

        # 1. 背景
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # 2. 立ち絵
        if self.char_image:
            rect = self.char_image.get_rect(midbottom=CHAR_POS)
            screen.blit(self.char_image, rect)

        # 3. テキストウィンドウ
        self._draw_text_window(screen)

    def _draw_text_window(self, screen):
        """現在表示中のテキストと話者名を描画"""
        if self.index >= len(self.script):
            return

        data = self.script[self.index]
        text = data.get("text", "")
        speaker = data.get("speaker", "")

        lines = []
        if speaker:
            lines.append(f"【{speaker}】")
        lines.append(text)

        draw_window(screen, self.font, lines, rect=TEXT_BOX_RECT)

    def end_scene(self):
        """ノベルパートを終了し、RPGパートへ遷移する"""
        self.active = False
        self.app.start_rpg_game()
