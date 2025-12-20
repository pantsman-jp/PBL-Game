"""
フィールド管理 | src/core/field.py
プレイヤー移動、NPC描画、マップ遷移、画面遷移時アニメーション、BGM管理
"""

import pygame
import os
import math
from src.utils import load_json, resource_path

TILE = 16
SCREEN_CENTER_X = 320
SCREEN_CENTER_Y = 200


class Field:
    def __init__(self, app):
        self.app = app
        self.moving = False
        self.dx = 0
        self.dy = 0
        self.offset = 0
        self.speed = 4
        self.map_image = None
        self.transitioning = False
        self.transition_radius = 0
        self.transition_target_map_id = None
        self.transition_dest_pos = None
        self._transition_stage = None
        self.transition_max_radius = math.hypot(SCREEN_CENTER_X, SCREEN_CENTER_Y)
        self.transition_speed = 4
        self.BASE_DIR = resource_path("assets")
        maps_path = resource_path(os.path.join(self.BASE_DIR, "data", "maps.json"))
        self.map_data = load_json(maps_path) or {}
        self.current_map_id = None
        self.current_walls = set()
        self.current_exits = {}
        self.load_map("world")
        self.load_player()
        self.dir = "front"

    def update(self, keys):
        if self.transitioning:
            self._update_transition()
            return
        if self.moving:
            self.offset += self.speed
            if self.offset >= TILE:
                self.offset = 0
                self.moving = False
                self.app.x += self.dx
                self.app.y += self.dy
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
        nx = self.app.x + dx
        ny = self.app.y + dy
        if nx < 0 or ny < 0 or nx >= self.map_w or ny >= self.map_h:
            return
        if (nx, ny) in self.current_walls:
            self._update_dir(dx, dy)
            return
        for _, data in self.app.talk.dialogues.items():
            if data.get("map_id") == self.current_map_id:
                pos = data.get("position")
                if pos and pos[0] == nx and pos[1] == ny:
                    self._update_dir(dx, dy)
                    return
        self._update_dir(dx, dy)
        self.dx = dx
        self.dy = dy
        self.moving = True
        self.offset = 0

    def _update_dir(self, dx, dy):
        if dy == 1:
            self.dir = "front"
        elif dy == -1:
            self.dir = "back"
        elif dx == 1:
            self.dir = "right"
        elif dx == -1:
            self.dir = "left"

    def draw(self, screen):
        if not self.map_image:
            return
        ox = self.offset * (-self.dx)
        oy = self.offset * (-self.dy)
        base_x = SCREEN_CENTER_X - self.app.x * TILE
        base_y = SCREEN_CENTER_Y - self.app.y * TILE
        screen.blit(self.map_image, (base_x + ox, base_y + oy))
        if self.dir == "front":
            self.player_image = self.player_front
        elif self.dir == "back":
            self.player_image = self.player_back
        elif self.dir == "right":
            self.player_image = self.player_right
        elif self.dir == "left":
            self.player_image = self.player_left
        screen.blit(self.player_image, self.player_rect)
        for _, data in self.app.talk.dialogues.items():
            if data.get("map_id") != self.current_map_id:
                continue
            pos = data.get("position")
            if not pos or len(pos) < 2:
                continue
            nx, ny = pos[0], pos[1]
            movement_config = data.get("movement_x", {})
            if "offset_x" not in data and movement_config.get("enabled", False):
                data["offset_x"] = 0
                data["NPC_speed"] = movement_config.get("speed", 0.5)
                data["max_offset_x"] = movement_config.get("max_offset", 8)
            if "offset_x" in data:
                data["offset_x"] += data["NPC_speed"]
                if abs(data["offset_x"]) > data["max_offset_x"]:
                    data["NPC_speed"] *= -1
                screen_x = (
                    SCREEN_CENTER_X + (nx - self.app.x) * TILE + ox + data["offset_x"]
                )
            else:
                screen_x = SCREEN_CENTER_X + (nx - self.app.x) * TILE + ox
            screen_y = SCREEN_CENTER_Y + (ny - self.app.y) * TILE + oy
            img_name = data.get("image")
            if img_name:
                if "image_surface" not in data:
                    img_path = resource_path(
                        os.path.join(self.BASE_DIR, "img", img_name)
                    )
                    if os.path.isfile(img_path):
                        surf = pygame.image.load(img_path).convert_alpha()
                        data["image_surface"] = pygame.transform.scale(
                            surf, (TILE, TILE)
                        )
                    else:
                        data["image_surface"] = None
                npc_image = data.get("image_surface")
                if npc_image:
                    screen.blit(npc_image, (screen_x, screen_y))
            lines = data.get("lines", [""])
            if lines:
                label_surf = self.app.font.render(lines[0][:12], True, (255, 255, 255))
                screen.blit(label_surf, (screen_x, screen_y - 18))
        if self.transitioning:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255))
            pygame.draw.circle(
                overlay,
                (0, 0, 0, 0),
                (SCREEN_CENTER_X, SCREEN_CENTER_Y),
                int(self.transition_radius),
            )
            screen.blit(overlay, (0, 0))
        coord_text = f"Map: {self.current_map_id} | ({self.app.x}, {self.app.y})"
        for ox, oy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            surf = self.app.font.render(coord_text, True, (0, 0, 0))
            screen.blit(surf, (8 + ox, 8 + oy))
        surf = self.app.font.render(coord_text, True, (255, 255, 255))
        screen.blit(surf, (8, 8))

    def _check_map_event(self):
        current_pos = (self.app.x, self.app.y)
        if current_pos in self.current_exits:
            exit_data = self.current_exits[current_pos]
            self._start_transition(
                exit_data["target_map"],
                exit_data.get("dest_x"),
                exit_data.get("dest_y"),
            )

    def _start_transition(self, map_id, dest_x, dest_y):
        self.transitioning = True
        self.transition_radius = self.transition_max_radius
        self.transition_target_map_id = map_id
        self.transition_dest_pos = (dest_x, dest_y)
        self._transition_stage = "out"

    def _update_transition(self):
        if self._transition_stage == "out":
            self.transition_radius -= self.transition_speed
            if self.transition_radius <= 0:
                self.load_map(self.transition_target_map_id)
                if self.transition_dest_pos:
                    self.app.x, self.app.y = self.transition_dest_pos
                self.transition_radius = 0
                self._transition_stage = "in"
        elif self._transition_stage == "in":
            self.transition_radius += self.transition_speed
            if self.transition_radius >= self.transition_max_radius:
                self.transition_radius = self.transition_max_radius
                self.transitioning = False
                self._transition_stage = None

    def load_map(self, map_id):
        if map_id not in self.map_data:
            print(f"Map ID not found: {map_id}")
            return
        self.current_map_id = map_id
        data = self.map_data[map_id]
        img_name = data.get("image", "world_map.png")
        path = resource_path(os.path.join(self.BASE_DIR, "img", img_name))
        if os.path.isfile(path):
            self.map_image = pygame.image.load(path).convert()
            w, h = self.map_image.get_size()
            self.map_w = w // TILE
            self.map_h = h // TILE
        else:
            self.map_image = None
            self.map_w = 0
            self.map_h = 0
        self.current_walls = set(tuple(w) for w in data.get("walls", []))
        self.current_exits = {(e["x"], e["y"]): e for e in data.get("exits", [])}
        bgm_file = data.get("bgm", "")
        if bgm_file:
            bgm_path = resource_path(os.path.join(self.BASE_DIR, "sounds", bgm_file))
            if os.path.isfile(bgm_path):
                try:
                    self.app.system.play_bgm(bgm_path)
                except Exception as e:
                    print("BGM再生エラー:", e)

    def load_player(self):
        front = resource_path(os.path.join(self.BASE_DIR, "img", "player_front.png"))
        back = resource_path(os.path.join(self.BASE_DIR, "img", "player_back.png"))
        right = resource_path(os.path.join(self.BASE_DIR, "img", "player_right.png"))
        if os.path.isfile(front):
            self.player_front = pygame.image.load(front).convert_alpha()
            self.player_front = pygame.transform.scale(self.player_front, (TILE, TILE))
        else:
            self.player_front = pygame.Surface((TILE, TILE))
            self.player_front.fill((255, 0, 0))
        if os.path.isfile(back):
            self.player_back = pygame.image.load(back).convert_alpha()
            self.player_back = pygame.transform.scale(self.player_back, (TILE, TILE))
        else:
            self.player_back = pygame.Surface((TILE, TILE))
            self.player_back.fill((0, 255, 0))
        if os.path.isfile(right):
            self.player_right = pygame.image.load(right).convert_alpha()
            self.player_right = pygame.transform.scale(self.player_right, (TILE, TILE))
        else:
            self.player_right = pygame.Surface((TILE, TILE))
            self.player_right.fill((0, 0, 255))
        self.player_left = pygame.transform.flip(self.player_right, True, False)
        self.player_image = self.player_front
        self.player_rect = self.player_image.get_rect(
            topleft=(SCREEN_CENTER_X, SCREEN_CENTER_Y)
        )
