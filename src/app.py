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
from src.ui import draw_objective_bar

WIDTH, HEIGHT = 900, 700
FPS = 60
SCENE_TITLE = 0
SCENE_GAME = 1
SCENE_VN = 2
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
        font_p = resource_path(
            os.path.join(BASE_DIR, "fonts", "NotoSansJP-Regular.ttf")
        )
        is_f = os.path.isfile(font_p)
        self.font = (
            pygame.font.Font(font_p, 16) if is_f else pygame.font.SysFont("meiryo", 16)
        )
        self.title_font = (
            pygame.font.Font(font_p, 32) if is_f else pygame.font.SysFont("meiryo", 32)
        )
        self.prompt_font = (
            pygame.font.Font(font_p, 20) if is_f else pygame.font.SysFont("meiryo", 20)
        )
        img_p = resource_path(os.path.join(BASE_DIR, "img", "title.jpg"))
        self.title_image = (
            pygame.image.load(img_p).convert() if os.path.isfile(img_p) else None
        )
        self.x, self.y, self.items, self._prev_item_count, self.inventory_open = (
            200,
            100,
            [],
            0,
            False,
        )
        self.field = Field(self)
        self.talk = Talk(self)
        self.vn = VisualNovel(self)
        self.scene_state = SCENE_TITLE
        self.running = True
        self.sfx_inv_open = self._load_sound("chestopen.mp3")
        self.sfx_inv_close = self._load_sound("chestclose.mp3")

    def _load_sound(self, name):
        p = resource_path(os.path.join(BASE_DIR, "sounds", name))
        if os.path.isfile(p):
            try:
                return pygame.mixer.Sound(p)
            except Exception:
                return None
        return None

    def start_game(self):
        self.scene_state = SCENE_VN
        self.vn.start("opening")

    def start_rpg_game(self):
        self.field.load_map("world")
        self.field.load_player()
        self.scene_state = SCENE_GAME

    def run(self):
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
        for ev in events:
            if ev.type == pygame.QUIT or (
                ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE
            ):
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
        if self.scene_state == SCENE_GAME:
            keys = self.key_tracker.update()
            self.talk.update(keys)
            if len(self.items) > self._prev_item_count:
                if hasattr(self.talk, "active"):
                    self.talk.active = False
                elif hasattr(self.talk, "_active"):
                    self.talk._active = False
            self.field.update(keys)
            self._prev_item_count = len(self.items)

    def _draw(self):
        if self.scene_state == SCENE_TITLE:
            if self.title_image:
                self.screen.blit(
                    self.title_image,
                    self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2)),
                )
            else:
                self.screen.fill((20, 20, 40))
                t_surf = self.title_font.render(
                    "Tiny Quiz Field", True, (255, 255, 255)
                )
                self.screen.blit(
                    t_surf, t_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                )
            if pygame.time.get_ticks() % 1000 < 500:
                p_surf = self.prompt_font.render(
                    "CLICK TO START", True, (255, 255, 200)
                )
                self.screen.blit(
                    p_surf, p_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80))
                )
        elif self.scene_state == SCENE_VN:
            self.vn.draw(self.screen)
        elif self.scene_state == SCENE_GAME:
            self.screen.fill((50, 50, 80))
            self.field.draw(self.screen)
            draw_objective_bar(
                self.screen,
                self.font,
                self.system.get_current_objective(),
                rect=(0, 0, WIDTH, 32),
            )
            i_text = "ITEMS: " + ", ".join(self.items) if self.items else "ITEMS: -"
            self.screen.blit(self.font.render(i_text, True, (255, 255, 255)), (8, 40))
            h_lines = ["Z : 話しかける / 決定", "Q : 会話を終了", "I : インベントリ"]
            for i, text in enumerate(h_lines):
                self.screen.blit(
                    self.font.render(text, True, (220, 220, 220)), (8, 64 + i * 18)
                )
            self.talk.draw(self.screen, self.font)
            if self.inventory_open:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                bx, by = (WIDTH - 480) // 2, (HEIGHT - 360) // 2
                pygame.draw.rect(self.screen, (30, 30, 40), (bx, by, 480, 360))
                pygame.draw.rect(self.screen, (200, 200, 200), (bx, by, 480, 360), 2)
                self.screen.blit(
                    self.title_font.render(
                        "INVENTORY (I to close)", True, (255, 255, 255)
                    ),
                    (bx + 12, by + 8),
                )
                for i, item in enumerate(self.items):
                    self.screen.blit(
                        self.font.render(f"- {item}", True, (220, 220, 220)),
                        (bx + 16, by + 48 + i * 22),
                    )
