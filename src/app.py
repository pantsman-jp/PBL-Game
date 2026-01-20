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

# --- ウィンドウ設定 ---
WIDTH, HEIGHT = 900, 700
FPS = 60

# --- シーン定義 ---
SCENE_TITLE = 0
SCENE_GAME = 1
SCENE_VN = 2


class App:
    def __init__(self):
        # pre_init は pygame.init() より前に呼ぶ
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        # 既に pygame.init() で mixer が初期化されている場合があるため確認
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        print("Mixer init status:", pygame.mixer.get_init())
        # 0. 基礎変数を「最初」に定義する（AttributeError防止）
        self.running = True
        self.scene_state = SCENE_TITLE
        self.iris_active = False
        self.iris_progress = 0.0
        self.iris_out = True
        self.iris_callback = None
        self.inventory_open = False
        self.x, self.y, self.items = 200, 100, []
        self._prev_item_count = 0
        self.stop_map_transition = None  # ノベル終了後のマップ遷移用
        self.played_events = set()  # 実行済みイベントIDを管理

        # Mixer 初期化
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            print("App: Mixer initialized successfully with directsound.")
        except Exception as e:
            print(f"App: Mixer initialization failed - {e}")

        # 2. 基本システム
        self.BASE_DIR = resource_path("assets")
        self.system = System(self)
        self.key_tracker = KeyTracker()

        # 3. 画面初期化
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tiny Quiz Field")
        self.clock = pygame.time.Clock()

        # 4. リソースロード
        self._load_resources()

        # 5. サブシステム（BGMを鳴らそうとする可能性があるもの）
        # ここで内部的にBGM再生が呼ばれても良いように、最後に配置
        self.field = Field(self)
        self.talk = Talk(self)
        self.vn = VisualNovel(self)

    def _load_resources(self):
        """フォントやタイトル画像などの静的リソースをロード"""
        font_p = resource_path(
            os.path.join(self.BASE_DIR, "fonts", "NotoSansJP-Regular.ttf")
        )
        is_f = os.path.isfile(font_p)

        # フォント設定
        if is_f:
            self.font = pygame.font.Font(font_p, 16)
            self.title_font = pygame.font.Font(font_p, 32)
            self.prompt_font = pygame.font.Font(font_p, 20)
        else:
            self.font = pygame.font.SysFont("meiryo", 16)
            self.title_font = pygame.font.SysFont("meiryo", 32)
            self.prompt_font = pygame.font.SysFont("meiryo", 20)

        #  タイトル画像
        img_p = resource_path(os.path.join(self.BASE_DIR, "img", "story", "title.jpg"))
        self.title_image = (
            pygame.image.load(img_p).convert() if os.path.isfile(img_p) else None
        )

        # 効果音
        self.sfx_inv_open = self._load_sound("chestopen.mp3")
        self.sfx_inv_close = self._load_sound("chestclose.mp3")

    def _load_sound(self, name):
        """指定された名前のサウンドファイルをロード"""
        p = resource_path(os.path.join(self.BASE_DIR, "sounds", name))
        if os.path.isfile(p):
            try:
                return pygame.mixer.Sound(p)
            except Exception:
                return None
        return None

    # --- シーン遷移制御 ---

    def start_game(self):
        """タイトルからVN（オープニング）を開始"""
        self.scene_state = SCENE_VN
        self.vn.start("opening")

    def start_rpg_game(self):
        """RPGパートを開始"""
        if self.stop_map_transition:
            map_id, dest_x, dest_y = self.stop_map_transition
            self.field._start_transition(map_id, dest_x, dest_y)
            self.stop_map_transition = None
        elif self.field.current_map_id is None:
            # マップがロードされていない場合のみデフォルトマップをロード
            self.field.load_map("world")

        self.field.load_player()
        self.scene_state = SCENE_GAME

    # --- メインループ ---

    def run(self):
        """ゲームのメインループ"""
        while self.running:
            self.clock.tick(FPS)

            events = pygame.event.get()
            self._handle_events(events)
            self._update()
            self._draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # --- イベント・更新処理 ---

    def _handle_events(self, events):
        """イベントハンドリングの振り分け"""
        for ev in events:
            if ev.type == pygame.QUIT or (
                ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE
            ):
                self.running = False

        if self.scene_state == SCENE_TITLE:
            if any(ev.type == pygame.MOUSEBUTTONDOWN for ev in events):
                self.start_game()

        elif self.scene_state == SCENE_VN:
            self.vn.update(events)

        elif self.scene_state == SCENE_GAME:
            self._handle_game_events(events)

    def _handle_game_events(self, events):
        """ゲーム中のキー入力イベント"""
        for ev in events:
            if ev.type != pygame.KEYDOWN:
                continue

            if ev.key == pygame.K_s:
                self.system.save()
            elif ev.key == pygame.K_i:
                self._toggle_inventory()

    def _toggle_inventory(self):
        """インベントリの開閉とSE再生"""
        self.inventory_open = not self.inventory_open
        sfx = self.sfx_inv_open if self.inventory_open else self.sfx_inv_close
        if sfx:
            try:
                sfx.play()
            except Exception:
                pass

    def _update(self):
        """データ更新の振り分け"""
        keys = self.key_tracker.update()

        if self.scene_state == SCENE_GAME:
            self.talk.update(keys)

        # アイテム獲得時に会話を安全に終了させる処理
        if len(self.items) > self._prev_item_count:
            # self.talk.request_close()  # ← このメソッドは無いので消してOKです
            pass

        # 会話中はプレイヤー更新を止める
        if not self.talk.is_active():
            self.field.update(keys)

        self._prev_item_count = len(self.items)

    # --- 描画処理 ---

    def _draw(self):
        """画面描画の振り分け"""
        if self.scene_state == SCENE_TITLE:
            self._draw_title()
        elif self.scene_state == SCENE_VN:
            self.vn.draw(self.screen)
        elif self.scene_state == SCENE_GAME:
            self._draw_game()

    def _draw_title(self):
        """タイトル画面の描画"""
        if self.title_image:
            self.screen.blit(
                self.title_image,
                self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2)),
            )
        else:
            self.screen.fill((20, 20, 40))
            t_surf = self.title_font.render("Tiny Quiz Field", True, (255, 255, 255))
            self.screen.blit(
                t_surf, t_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            )

        # 点滅するプロンプト
        if pygame.time.get_ticks() % 1000 < 500:
            p_surf = self.prompt_font.render("CLICK TO START", True, (255, 255, 200))
            self.screen.blit(p_surf, p_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80)))

    def _draw_game(self):
        """RPGパートの描画"""
        self.screen.fill((50, 50, 80))
        self.field.draw(self.screen)

        # UI: 目的バー
        draw_objective_bar(
            self.screen,
            self.font,
            self.system.get_current_objective(),
            rect=(0, 0, WIDTH, 32),
        )

        # UI: アイテムリスト
        i_text = f"ITEMS: {', '.join(self.items)}" if self.items else "ITEMS: -"
        self.screen.blit(self.font.render(i_text, True, (255, 255, 255)), (8, 40))

        # UI: 座標表示
        pos_text = f"POS: ({self.x}, {self.y})"
        self.screen.blit(self.font.render(pos_text, True, (255, 255, 255)), (8, 64))

        # UI: 操作ガイド
        h_lines = [
            "Z : 話しかける / 決定",
            "Q : 会話を終了",
            "I : インベントリ",
            "M : マップを開く",
        ]
        for i, text in enumerate(h_lines):
            self.screen.blit(
                self.font.render(text, True, (220, 220, 220)), (8, 88 + i * 18)
            )

        # 会話ウィンドウ
        self.talk.draw(self.screen, self.font)

        # インベントリ・オーバーレイ
        if self.inventory_open:
            self._draw_inventory()

    def _draw_inventory(self):
        """インベントリ画面のオーバーレイ描画"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # ウィンドウ本体
        bx, by = (WIDTH - 480) // 2, (HEIGHT - 360) // 2
        pygame.draw.rect(self.screen, (30, 30, 40), (bx, by, 480, 360))
        pygame.draw.rect(self.screen, (200, 200, 200), (bx, by, 480, 360), 2)

        # テキスト描画
        self.screen.blit(
            self.title_font.render("INVENTORY (I to close)", True, (255, 255, 255)),
            (bx + 12, by + 8),
        )
        for i, item in enumerate(self.items):
            self.screen.blit(
                self.font.render(f"- {item}", True, (220, 220, 220)),
                (bx + 16, by + 48 + i * 22),
            )
