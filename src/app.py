"""
アプリケーションクラス | src/app.py
ウィンドウ初期化、サブモジュール生成、BGM再生、メインループを担当
"""

import os
import pygame
import sys
from src.utils import KeyTracker, resource_path
from src.core.system import System
from src.core.field import Field
from src.core.talk import Talk
from src.core.visual_novel import VisualNovel

WIDTH, HEIGHT = 900, 700
FPS = 60

# --- シーン定数 (Scene Constants) ---
# ゲームの状態を管理する値
# メインループ内でこの値をチェックし、描画や更新処理を切り替え
SCENE_TITLE = 0  # タイトル画面
SCENE_GAME = 1  # RPGパート
SCENE_VN = 2  # ノベルパート


BASE_DIR = resource_path("assets")


class App:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass

        self.system = System(self)

        self.key_tracker = KeyTracker()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tiny Quiz Field - pygame")
        self.clock = pygame.time.Clock()

        # --- フォント設定 ---
        font_path = resource_path(
            os.path.join(BASE_DIR, "fonts", "NotoSansJP-Regular.otf")
        )
        if os.path.isfile(font_path):
            self.font = pygame.font.Font(font_path, 16)
            self.title_font = pygame.font.Font(font_path, 32)
            self.prompt_font = pygame.font.Font(font_path, 20)
        else:
            self.font = pygame.font.SysFont("meiryo", 16)
            self.title_font = pygame.font.SysFont("meiryo", 32)
            self.prompt_font = pygame.font.SysFont("meiryo", 20)

        # --- タイトル画像 ---
        title_img_path = resource_path(os.path.join(BASE_DIR, "img", "title.jpg"))
        self.title_image = (
            pygame.image.load(title_img_path).convert()
            if os.path.isfile(title_img_path)
            else None
        )

        # --- プレイヤー初期座標とインベントリ ---
        self.x = 200
        self.y = 100
        self.items = []
        self._prev_item_count = 0  # ★ アイテム増加検知用
        self.inventory_open = False

        # --- サブモジュール生成 ---
        self.field = Field(self)
        self.talk = Talk(self)
        self.vn = VisualNovel(self)

        self.scene_state = SCENE_TITLE
        self.running = True

        # --- 効果音ロード ---
        def _load_sound(name):
            p = resource_path(os.path.join(BASE_DIR, "sounds", name))
            if os.path.isfile(p):
                try:
                    return pygame.mixer.Sound(p)
                except Exception:
                    return None
            return None

        self.sfx_inv_open = _load_sound("chestopen.mp3")
        self.sfx_inv_close = _load_sound("chestclose.mp3")

    def start_game(self):
        """
        - ゲームを開始
            - タイトル画面でのクリック後にノベルパート開始
<<<<<<< Updated upstream

        - 開発用：ノベルパートの再生はここの変数を変更してください
        """
        self.scene_state = SCENE_VN
        self.vn.start("ending")  # 開発用
=======
        - 開発用：ノベルパートの再生はここの変数を変更してください
        """

        self.scene_state = (
            SCENE_VN  # タイトル画面からクリックされたら、まずノベルパートを開始
        )
        self.vn.start("opening")
>>>>>>> Stashed changes

    def start_rpg_game(self):
        """
        RPGパート開始
        """
        self.field.load_map("world")
        self.field.load_player()
        self.scene_state = SCENE_GAME

    def run(self):
        """
        - アプリケーションのメインループ
            - 終了フラグが立つまで、イベント処理、更新、描画を繰り返す
        """
        while self.running:
            self.clock.tick(FPS)
            events = pygame.event.get()
            self._handle_events(events)
            self._update()
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def _handle_events(self, events):
        """
        - Pygameのイベント（キー入力、マウス操作、ウィンドウ閉じるなど）を処理
            - 現在のシーンに応じて処理を振り分け
        """
        for ev in events:
            if ev.type == pygame.QUIT:
                self.running = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.running = False

        if self.scene_state == SCENE_TITLE:
            for ev in events:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    self.start_game()
        elif self.scene_state == SCENE_VN:
            self.vn.update(events)
        elif self.scene_state == SCENE_GAME:
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_s:
                        self.system.save()
                    if ev.key == pygame.K_i:
                        self.inventory_open = not self.inventory_open
                        try:
                            if self.inventory_open and self.sfx_inv_open:
                                self.sfx_inv_open.play()
                            elif not self.inventory_open and self.sfx_inv_close:
                                self.sfx_inv_close.play()
                        except Exception:
                            pass

    def _update(self):
        """
        - ゲーム状態の更新（毎フレーム呼び出し）
            - 現在のシーンに応じて、各モジュールのupdateメソッドを呼び出す
        """
        if self.scene_state == SCENE_TITLE:
            pass
        elif self.scene_state == SCENE_VN:
            pass
        elif self.scene_state == SCENE_GAME:
            keys = self.key_tracker.update()
            self.talk.update(keys)

            # ★ アイテム取得後は会話を自動終了
            if len(self.items) > self._prev_item_count:
                # ★ talk.end() はゲーム終了を引き起こすため使わない
                if hasattr(self.talk, "active"):
                    self.talk.active = False
            elif hasattr(self.talk, "_active"):
                self.talk._active = False

            self.field.update(keys)
            self._prev_item_count = len(self.items)

    def _draw(self):
        if self.scene_state == SCENE_TITLE:
            if self.title_image:
                rect = self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(self.title_image, rect)
            else:
                self.screen.fill((20, 20, 40))
                title_surf = self.title_font.render(
                    "Tiny Quiz Field", True, (255, 255, 255)
                )
                rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                self.screen.blit(title_surf, rect)

            if pygame.time.get_ticks() % 1000 < 500:
                prompt_surf = self.prompt_font.render(
                    "CLICK TO START", True, (255, 255, 200)
                )
                rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80))
                self.screen.blit(prompt_surf, rect)

        elif self.scene_state == SCENE_VN:
            self.vn.draw(self.screen)

        elif self.scene_state == SCENE_GAME:
            self.screen.fill((50, 50, 80))
            self.field.draw(self.screen)

            # 所持アイテム表示
            items_text = "ITEMS: " + ", ".join(self.items) if self.items else "ITEMS: -"
            surf = self.font.render(items_text, True, (255, 255, 255))

            self.screen.blit(surf, (8, 40))

            # ★ 操作説明表示
            help_lines = [
                "Z : 話しかける / 決定",
                "Q : 会話を終了",
                "I : インベントリ",
            ]
            for i, text in enumerate(help_lines):
                help_surf = self.font.render(text, True, (220, 220, 220))
                self.screen.blit(help_surf, (8, 64 + i * 18))

            self.talk.draw(self.screen, self.font)

            # インベントリ表示
            if self.inventory_open:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                box_w, box_h = 480, 360
                bx = (WIDTH - box_w) // 2
                by = (HEIGHT - box_h) // 2
                pygame.draw.rect(self.screen, (30, 30, 40), (bx, by, box_w, box_h))
                pygame.draw.rect(
                    self.screen, (200, 200, 200), (bx, by, box_w, box_h), 2
                )
                title_surf = self.title_font.render(
                    "INVENTORY (I to close)", True, (255, 255, 255)
                )
                self.screen.blit(title_surf, (bx + 12, by + 8))
                for i, item in enumerate(self.items):
                    it_surf = self.font.render(f"- {item}", True, (220, 220, 220))
                    self.screen.blit(it_surf, (bx + 16, by + 48 + i * 22))
