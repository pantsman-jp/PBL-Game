"""
フィールド管理 | src/core/field.py
プレイヤー移動、NPC描画、マップ遷移、画面遷移時アニメーション、BGM管理
"""

import pygame
import os
import math
from src.utils import load_json, resource_path

# 定数定義：タイルサイズおよび画面中心座標
TILE = 10
ZOOM = 2
Z_TILE = TILE * ZOOM
SCREEN_CENTER_X = 900 // 2
SCREEN_CENTER_Y = 700 // 2
# 累積的なずれを補正するための定数
Y_OFFSET = 1.0
Y_DRIFT = 0.0


class Field:
    """
    フィールドの管理、描画、移動判定、マップ遷移を制御する
    """

    def __init__(self, app):
        """
        フィールドクラスを初期化し、マップデータとプレイヤーの読み込み
        """
        self.app = app
        self.moving = False
        self.dx = 0
        self.dy = 0
        self.offset = 0
        self.speed = 2
        self.map_image = None
        self.map_pixels = None
        self.map_pixel_w = 0
        self.map_pixel_h = 0
        self.transitioning = False
        self.transition_radius = 0
        self.transition_target_map_id = None
        self.transition_dest_pos = None
        self._transition_stage = None
        self.transition_max_radius = math.hypot(SCREEN_CENTER_X, SCREEN_CENTER_Y)
        self.transition_speed = 8
        self.BASE_DIR = resource_path("assets")
        maps_path = resource_path(os.path.join(self.BASE_DIR, "data", "maps.json"))
        self.map_data = load_json(maps_path) or {}
        self.current_map_id = None
        self.current_exits = {}
        self.load_map("world")
        self.load_player()
        self.dir = "front"

    def _is_sea_color(self, r, g, b):
        """
        指定されたRGB値が海のタイル（白波を含む）に該当するか判定
        """
        return r < 25 and 90 <= g <= 155 and b >= 230

    def _can_move_pixel(self, world_px, world_py):
        """
        補正後の座標の周囲3x3ピクセルを確認し、移動可能か判定
        """
        if self.map_pixels is None:
            return True
        px, w, h, cx, cy = (
            self.map_pixels,
            self.map_pixel_w,
            self.map_pixel_h,
            int(world_px),
            int(world_py),
        )
        if cx < 1 or cy < 1 or cx >= w - 1 or cy >= h - 1:
            return False
        return not any(
            self._is_sea_color(*px[x][y])
            for x in range(cx - 1, cx + 2)
            for y in range(cy - 1, cy + 2)
        )

    def update(self, keys):
        """
        プレイヤーの入力状態と移動アニメーション、マップイベントの更新
        """
        if self.transitioning:
            self._update_transition()
            return
        if self.moving:
            self.offset += self.speed
            if self.offset >= TILE:
                self.app.x, self.app.y, self.moving, self.offset = (
                    self.app.x + self.dx,
                    self.app.y + self.dy,
                    False,
                    0,
                )
                self._check_map_event()
            return
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.start_move(0, -1)
        elif pressed[pygame.K_DOWN]:
            self.start_move(0, 1)
        elif pressed[pygame.K_LEFT]:
            self.start_move(-1, 0)
        elif pressed[pygame.K_RIGHT]:
            self.start_move(1, 0)
        elif keys.get("z"):
            self.app.talk.try_talk()

    def start_move(self, dx, dy):
        """
        補正係数を考慮した座標で通行可能か判定し、移動を開始
        """
        nx, ny = self.app.x + dx, self.app.y + dy
        if nx < 0 or ny < 0 or nx >= self.map_w or ny >= self.map_h:
            return
        if any(
            d.get("position") == [nx, ny]
            for d in self.app.talk.dialogues.values()
            if d.get("map_id") == self.current_map_id
        ):
            self._update_dir(dx, dy)
            return
        # 垂直方向の累積誤差を考慮したサンプリング座標の計算
        # 公式: world_py = ny * TILE + 5 + Y_OFFSET + (ny * Y_DRIFT)
        adj_py = ny * TILE + 5 + Y_OFFSET + (ny * Y_DRIFT)
        if not self._can_move_pixel(nx * TILE + 5, adj_py):
            self._update_dir(dx, dy)
            return
        self._update_dir(dx, dy)
        self.dx, self.dy, self.moving, self.offset = dx, dy, True, 0

    def _update_dir(self, dx, dy):
        """
        移動方向に基づいてプレイヤーの向きを更新
        """
        self.dir = (
            "front"
            if dy == 1
            else "back"
            if dy == -1
            else "right"
            if dx == 1
            else "left"
            if dx == -1
            else self.dir
        )

    def draw(self, screen):
        """
        マップ、NPC、プレイヤー、座標情報を画面に描画
        """
        if not self.map_image:
            return
        ox, oy = self.offset * (-self.dx) * ZOOM, self.offset * (-self.dy) * ZOOM
        base_x, base_y = (
            SCREEN_CENTER_X - self.app.x * Z_TILE,
            SCREEN_CENTER_Y - self.app.y * Z_TILE,
        )
        screen.blit(self.map_image_zoom, (base_x + ox, base_y + oy))
        self.player_image = getattr(self, f"player_{self.dir}")
        screen.blit(self.player_image, (SCREEN_CENTER_X, SCREEN_CENTER_Y))
        for _, data in self.app.talk.dialogues.items():
            if data.get("map_id") != self.current_map_id:
                continue
            pos = data.get("position")
            if not pos or len(pos) < 2:
                continue
            nx, ny = pos[0], pos[1]
            movement_config = data.get("movement_x", {})
            if "offset_x" not in data and movement_config.get("enabled", False):
                data["offset_x"], data["NPC_speed"], data["max_offset_x"] = (
                    0,
                    movement_config.get("speed", 0.5),
                    movement_config.get("max_offset", 8),
                )
            z_npc_offset = data.get("offset_x", 0) * ZOOM if "offset_x" in data else 0
            if "offset_x" in data:
                data["offset_x"] += data["NPC_speed"]
                if abs(data["offset_x"]) > data["max_offset_x"]:
                    data["NPC_speed"] *= -1
            screen_x = SCREEN_CENTER_X + (nx - self.app.x) * Z_TILE + ox + z_npc_offset
            screen_y = SCREEN_CENTER_Y + (ny - self.app.y) * Z_TILE + oy
            img_name = data.get("image")
            if img_name and "image_surface_zoom" not in data:
                img_path = resource_path(os.path.join(self.BASE_DIR, "img", img_name))
                data["image_surface_zoom"] = (
                    pygame.transform.scale(
                        pygame.image.load(img_path).convert_alpha(), (Z_TILE, Z_TILE)
                    )
                    if os.path.isfile(img_path)
                    else None
                )
            npc_image = data.get("image_surface_zoom")
            if npc_image:
                screen.blit(npc_image, (screen_x, screen_y))
            lines = data.get("lines", [""])
            if lines:
                label_surf = self.app.font.render(lines[0][:12], True, (255, 255, 255))
                screen.blit(label_surf, (screen_x, screen_y - 24))
        if self.transitioning:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255))
            pygame.draw.circle(
                overlay,
                (0, 0, 0, 0),
                (SCREEN_CENTER_X + Z_TILE // 2, SCREEN_CENTER_Y + Z_TILE // 2),
                int(self.transition_radius),
            )
            screen.blit(overlay, (0, 0))
        coord_text = f"Map: {self.current_map_id} | ({self.app.x}, {self.app.y})"
        [
            screen.blit(
                self.app.font.render(coord_text, True, (0, 0, 0)), (8 + ox2, 8 + oy2)
            )
            for ox2, oy2 in [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        ]
        screen.blit(self.app.font.render(coord_text, True, (255, 255, 255)), (8, 8))

    def _check_map_event(self):
        """
        現在のタイルに存在するマップ移動イベント（出口）を確認
        """
        if (self.app.x, self.app.y) in self.current_exits:
            exit_data = self.current_exits[(self.app.x, self.app.y)]
            self._start_transition(
                exit_data["target_map"],
                exit_data.get("dest_x"),
                exit_data.get("dest_y"),
            )

    def _start_transition(self, map_id, dest_x, dest_y):
        """
        マップ遷移アニメーションを開始
        """
        (
            self.transitioning,
            self.transition_radius,
            self.transition_target_map_id,
            self.transition_dest_pos,
            self._transition_stage,
        ) = (True, self.transition_max_radius, map_id, (dest_x, dest_y), "out")

    def _update_transition(self):
        """
        画面遷移の半径を更新し、フェードアウト完了時にマップを切り替え
        """
        if self._transition_stage == "out":
            self.transition_radius -= self.transition_speed
            if self.transition_radius <= 0:
                self.load_map(self.transition_target_map_id)
                if self.transition_dest_pos:
                    self.app.x, self.app.y = self.transition_dest_pos
                self.transition_radius, self._transition_stage = 0, "in"
        elif self._transition_stage == "in":
            self.transition_radius += self.transition_speed
            if self.transition_radius >= self.transition_max_radius:
                self.transition_radius, self.transitioning, self._transition_stage = (
                    self.transition_max_radius,
                    False,
                    None,
                )

    def load_map(self, map_id):
        """
        新しいマップデータを読み込み、画像タイルおよび衝突判定用のピクセル配列を作成
        """
        if map_id not in self.map_data:
            return
        self.current_map_id = map_id
        data = self.map_data[map_id]
        img_name, bgm_file = data.get("image", "map/world_map.png"), data.get("bgm", "")
        path = resource_path(os.path.join(self.BASE_DIR, "img", img_name))
        if os.path.isfile(path):
            self.map_image = pygame.image.load(path).convert()
            self.map_pixel_w, self.map_pixel_h = self.map_image.get_size()
            self.map_image_zoom = pygame.transform.scale(
                self.map_image, (self.map_pixel_w * ZOOM, self.map_pixel_h * ZOOM)
            )
            self.map_pixels = pygame.surfarray.array3d(self.map_image)
            self.map_w, self.map_h = self.map_pixel_w // TILE, self.map_pixel_h // TILE
        else:
            (
                self.map_image,
                self.map_image_zoom,
                self.map_pixels,
                self.map_w,
                self.map_h,
            ) = (None, None, None, 0, 0)
        self.current_exits = {(e["x"], e["y"]): e for e in data.get("exits", [])}
        if bgm_file:
            bgm_path = resource_path(os.path.join(self.BASE_DIR, "sounds", bgm_file))
            if os.path.isfile(bgm_path):
                try:
                    self.app.system.play_bgm(bgm_path)
                except Exception:
                    pass

    def _get_scaled_player_surface(self, path, color):
        """
        プレイヤー画像を読み込み、ズーム倍率に合わせてスケーリング
        """
        if os.path.isfile(path):
            return pygame.transform.scale(
                pygame.image.load(path).convert_alpha(), (Z_TILE, Z_TILE)
            )
        surf = pygame.Surface((Z_TILE, Z_TILE))
        surf.fill(color)
        return surf

    def load_player(self):
        """
        各方向のプレイヤー画像を読み込み
        """
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
        self.player_left = pygame.transform.flip(self.player_right, True, False)
        self.player_image = self.player_front
