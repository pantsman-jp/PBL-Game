"""
フィールド管理 | src/core/field.py
プレイヤー移動、NPC描画、マップ遷移、画面遷移時アニメーション、BGM管理
"""

import pygame
import os
import math
from src.utils import load_json, resource_path

# --- 定数設定 ---
TILE = 10
ZOOM = 2
Z_TILE = TILE * ZOOM
SCREEN_CENTER_X = 900 // 2
SCREEN_CENTER_Y = 700 // 2
Y_OFFSET = 1.0
Y_DRIFT = 0.0


class Field:
    """
    フィールドの管理、描画、移動判定、マップ遷移を制御するクラス
    """

    def __init__(self, app):
        self.app = app
        self.BASE_DIR = resource_path("assets")

        # 移動・座標関連
        self.moving = False
        self.dx = 0
        self.dy = 0
        self.offset = 0  # タイル間の移動進捗
        self.speed = 2  # 1フレームあたりの移動ピクセル
        self.dir = "front"

        # マップデータ関連
        self.map_image = None
        self.map_image_zoom = None
        self.map_pixels = None
        self.map_pixel_w = 0
        self.map_pixel_h = 0
        self.map_w = 0
        self.map_h = 0
        self.current_map_id = None
        self.current_exits = {}
        self.map_data = (
            load_json(resource_path(os.path.join(self.BASE_DIR, "data", "maps.json")))
            or {}
        )

        # 画面遷移（トランジション）関連
        self.transitioning = False
        self.transition_radius = 0
        self.transition_max_radius = math.hypot(SCREEN_CENTER_X, SCREEN_CENTER_Y)
        self.transition_speed = 8
        self._transition_stage = None  # "out" (暗転中) または "in" (明転中)
        self.transition_target_map_id = None
        self.transition_dest_pos = None

        # BGM管理
        self._current_bgm_path = None

        # 初期ロード
        self.load_map("world")
        self.load_player()

    # --- 判定ロジック ---

    def _is_sea_color(self, r, g, b):
        """ピクセルの色が海（移動不可領域）かどうかを判定"""
        return r < 25 and 90 <= g <= 155 and b >= 230

    def _can_move_pixel(self, world_px, world_py):
        """指定された座標が衝突判定（海など）に抵触しないか確認"""
        if self.map_pixels is None:
            return True

        px, w, h = self.map_pixels, self.map_pixel_w, self.map_pixel_h
        cx, cy = int(world_px), int(world_py)

        # マップ範囲外チェック
        if cx < 1 or cy < 1 or cx >= w - 1 or cy >= h - 1:
            return False

        # 周囲のピクセルを確認して判定
        return not any(
            self._is_sea_color(*px[x][y])
            for x in range(cx - 1, cx + 2)
            for y in range(cy - 1, cy + 2)
        )

    # --- 更新処理 ---

    def update(self, keys):
        """毎フレームの更新処理"""
        # 画面遷移中の場合は遷移アニメーションのみ更新
        if self.transitioning:
            self._update_transition()
            return

        # 会話中は移動不可
        if self.app.talk.is_active():
            return

        # 移動アニメーション中
        if self.moving:
            self._update_movement()
            return

        # キー入力受付
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            self.start_move(0, -1)
        elif pressed[pygame.K_s]:
            self.start_move(0, 1)
        elif pressed[pygame.K_a]:
            self.start_move(-1, 0)
        elif pressed[pygame.K_d]:
            self.start_move(1, 0)
        elif keys.get("z"):
            self.app.talk.try_talk()

    def _update_movement(self):
        """タイル間のスムーズな移動を更新"""
        self.offset += self.speed
        if self.offset >= TILE:
            # タイルへの到着
            self.app.x += self.dx
            self.app.y += self.dy
            self.moving = False
            self.offset = 0
            self._check_map_event()

    def start_move(self, dx, dy):
        """移動を開始する（衝突判定とNPCの存在確認）"""
        nx, ny = self.app.x + dx, self.app.y + dy

        # 境界チェック
        if nx < 0 or ny < 0 or nx >= self.map_w or ny >= self.map_h:
            return

        # 向きの更新
        self._update_dir(dx, dy)

        # NPCがいるかチェック
        for d in self.app.talk.dialogues.values():
            if d.get("map_id") == self.current_map_id and d.get("position") == [nx, ny]:
                return

        # 衝突判定（地形）
        adj_py = ny * TILE + 5 + Y_OFFSET + (ny * Y_DRIFT)
        if not self._can_move_pixel(nx * TILE + 5, adj_py):
            return

        # 移動開始フラグ
        self.dx, self.dy, self.moving, self.offset = dx, dy, True, 0

    def _update_dir(self, dx, dy):
        """プレイヤーの向きを更新"""
        if dy == 1:
            self.dir = "front"
        elif dy == -1:
            self.dir = "back"
        elif dx == 1:
            self.dir = "right"
        elif dx == -1:
            self.dir = "left"

    # --- 描画処理 ---

    def draw(self, screen):
        """フィールド全体の描画"""
        if not self.map_image:
            return

        # 移動中の滑らかな表示オフセット計算
        ox = self.offset * (-self.dx) * ZOOM
        oy = self.offset * (-self.dy) * ZOOM

        # マップの描画位置（プレイヤーを中心に据える）
        base_x = SCREEN_CENTER_X - self.app.x * Z_TILE
        base_y = SCREEN_CENTER_Y - self.app.y * Z_TILE
        screen.blit(self.map_image_zoom, (base_x + ox, base_y + oy))

        # NPCの描画
        self._draw_npcs(screen, base_x, base_y, ox, oy)

        # プレイヤーの描画
        self.player_image = getattr(self, f"player_{self.dir}")
        # プレイヤーを中央に描画
        screen.blit(
            self.player_image,
            (SCREEN_CENTER_X, SCREEN_CENTER_Y),
        )

        # 遷移アニメーションの描画（アイリスイン/アウト）
        if self.transitioning:
            # 画面サイズに合わせたサーフェス作成
            mask = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 255))  # まず全体を真っ黒にする

            # 円の部分だけを「透明」で上書き描画する
            # 第2引数の(0,0,0,0)が透明色（RGBA）
            pygame.draw.circle(
                mask,
                (0, 0, 0, 0),
                (SCREEN_CENTER_X, SCREEN_CENTER_Y),
                max(
                    0, int(self.transition_radius)
                ),  # 半径がマイナスにならないようガード
            )

            screen.blit(mask, (0, 0))

    def _draw_npcs(self, screen, base_x, base_y, ox, oy):
        """NPCの描画とアニメーション処理"""
        for _, data in self.app.talk.dialogues.items():
            if data.get("map_id") != self.current_map_id:
                continue

            pos = data.get("position")
            if not pos:
                continue

            nx, ny = pos

            # NPCの左右移動（浮遊アニメーション等）の更新
            z_npc_offset = self._update_npc_animation(data)

            # 画面上の座標計算
            screen_x = SCREEN_CENTER_X + (nx - self.app.x) * Z_TILE + ox + z_npc_offset
            screen_y = SCREEN_CENTER_Y + (ny - self.app.y) * Z_TILE + oy

            # 画像のロードとスケール（キャッシュ化）
            if "image_surface_zoom" not in data:
                img_name = data.get("image")
                if img_name:
                    path = resource_path(os.path.join(self.BASE_DIR, "img", img_name))
                    raw_img = pygame.image.load(path).convert_alpha()
                    data["image_surface_zoom"] = pygame.transform.scale(
                        raw_img, (Z_TILE, Z_TILE)
                    )

            npc_image = data.get("image_surface_zoom")
            if npc_image:
                screen.blit(npc_image, (screen_x, screen_y))

    def _update_npc_animation(self, data):
        """NPCの動き（offset_x）を計算して返す"""
        config = data.get("movement_x", {})
        if not config.get("enabled", False):
            return 0

        # 初期化
        if "offset_x" not in data:
            data["offset_x"] = 0
            data["NPC_speed"] = config.get("speed", 0.5)
            data["max_offset_x"] = config.get("max_offset", 8)

        # 移動更新
        data["offset_x"] += data["NPC_speed"]
        if abs(data["offset_x"]) > data["max_offset_x"]:
            data["NPC_speed"] *= -1

        return data["offset_x"] * ZOOM

    # --- マップ遷移処理 ---

    def _check_map_event(self):
        """現在の座標に出口があるかチェック"""
        pos = (self.app.x, self.app.y)
        if pos in self.current_exits:
            exit_data = self.current_exits[pos]
            self._start_transition(
                exit_data["target_map"],
                exit_data.get("dest_x"),
                exit_data.get("dest_y"),
            )

    def _start_transition(self, map_id, dest_x, dest_y):
        """遷移アニメーションの開始"""
        self.transitioning = True
        self.transition_radius = self.transition_max_radius
        self.transition_target_map_id = map_id
        self.transition_dest_pos = (dest_x, dest_y)
        self._transition_stage = "out"

    def _update_transition(self):
        """アイリスアウト（閉じる）/ アイリスイン（開く）のロジック"""
        if not self.transitioning:
            return
        if self._transition_stage == "out":
            # アイリスアウト：円が小さくなって画面が暗くなる
            self.transition_radius -= self.transition_speed
            if self.transition_radius <= 0:
                self.transition_radius = 0
                # マップ切り替え処理
                self.load_map(self.transition_target_map_id)
                if self.transition_dest_pos:
                    self.app.x, self.app.y = self.transition_dest_pos
                self._transition_stage = "in"

        elif self._transition_stage == "in":
            # アイリスイン：円が大きくなって画面が見えるようになる
            self.transition_radius += self.transition_speed
            if self.transition_radius >= self.transition_max_radius:
                self.transitioning = False
                self._transition_stage = None

    # --- リソースロード ---

    def load_map(self, map_id):
        """マップデータのロードと画像・BGMのセットアップ"""
        if map_id not in self.map_data:
            return

        self.current_map_id = map_id
        data = self.map_data[map_id]
        img_name = data.get("image", "map/world_map.png")
        path = resource_path(os.path.join(self.BASE_DIR, "img", img_name))
        self.map_image = pygame.image.load(path).convert()
        self.map_pixel_w, self.map_pixel_h = self.map_image.get_size()

        # 描画用拡大マップ作成
        self.map_image_zoom = pygame.transform.scale(
            self.map_image, (self.map_pixel_w * ZOOM, self.map_pixel_h * ZOOM)
        )

        # 衝突判定用のピクセル配列
        self.map_pixels = pygame.surfarray.array3d(self.map_image)
        self.map_w = self.map_pixel_w // TILE
        self.map_h = self.map_pixel_h // TILE

        # 出口データの整理
        self.current_exits = {(e["x"], e["y"]): e for e in data.get("exits", [])}

        # BGM更新
        self._update_bgm(data.get("bgm"))

    def _update_bgm(self, bgm_path):
        """マップデータに基づくBGMの更新"""
        if not pygame.mixer.get_init():
            return

        if not bgm_path:
            self.app.system.stop_bgm()
            return

        # sounds フォルダを含めた相対パスを作成して System に渡す
        target_path = os.path.join("assets", "sounds", bgm_path)
        print("DEBUG: _update_bgm called with", bgm_path)
        self.app.system.play_bgm(target_path)

    def _get_scaled_player_surface(self, path, color):
        """プレイヤー画像をロードし、なければ単色タイルを返す"""
        if os.path.isfile(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (Z_TILE, Z_TILE))

        surf = pygame.Surface((Z_TILE, Z_TILE))
        surf.fill(color)
        return surf

    def load_player(self):
        """全方向のプレイヤー画像をロード"""
        img_dir = os.path.join(self.BASE_DIR, "img")

        self.player_front = self._get_scaled_player_surface(
            resource_path(os.path.join(self.BASE_DIR, "img", "character", "player_front.png")),
            (255, 0, 0),
        )
        self.player_back = self._get_scaled_player_surface(
            resource_path(os.path.join(self.BASE_DIR, "img", "character", "player_back.png")),
            (0, 255, 0),
        )
        self.player_right = self._get_scaled_player_surface(
            resource_path(os.path.join(self.BASE_DIR, "img", "character", "player_right.png")),
            (0, 0, 255),
        )
        # 左向きは右向きの反転で対応
        self.player_left = pygame.transform.flip(self.player_right, True, False)
        self.player_image = self.player_front
