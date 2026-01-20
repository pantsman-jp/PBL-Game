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
        self.script_id = None
        self.script = []
        self.index = 0

        # 選択肢・クイズ管理
        self.waiting_for_choice = False
        self.choice_items = []
        self.choice_index = 0
        self.choice_rects = []  # ボタンの当たり判定用
        self.labels = {}  # ジャンプ用ラベルマップ

        # リソース管理
        self.bg_image = None
        self.char_image = None
        self.char_offset_y = 0  # 立ち絵のY座標オフセット
        self._image_cache = {}  # 重複ロード防止用のキャッシュ

        # データロード
        self.scripts_data = {}

        # 2. novel_scripts フォルダ内のJSONをロード・マージ
        scripts_dir = os.path.join(self.base_dir, "data", "novel_scripts")
        if os.path.isdir(scripts_dir):
            for filename in os.listdir(scripts_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(scripts_dir, filename)
                    data = load_json(file_path)
                    if data:
                        self.scripts_data.update(data)

        self.font = app.font
        self.ui_font = app.font

    def start(self, script_id):
        """指定されたIDのシナリオを開始する"""
        if script_id not in self.scripts_data:
            print(f"VisualNovel: Script ID '{script_id}' not found.")
            self.end_scene()
            return

        self.script_id = script_id
        self.script = self.scripts_data[script_id]
        self.index = 0
        self.active = True

        self._scan_labels()
        self._load_current_scene()

    def _scan_labels(self):
        """現在のスクリプト内のラベルをスキャンして記録"""
        self.labels = {}
        for i, data in enumerate(self.script):
            label = data.get("label")
            if label:
                self.labels[label] = i

    def update(self, events):
        """入力処理"""
        if not self.active:
            return

        for ev in events:
            # 選択肢選択モード
            if self.waiting_for_choice:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_UP:
                        self.choice_index = (self.choice_index - 1) % len(
                            self.choice_items
                        )
                    elif ev.key == pygame.K_DOWN:
                        self.choice_index = (self.choice_index + 1) % len(
                            self.choice_items
                        )
                    elif ev.key in (pygame.K_z, pygame.K_SPACE, pygame.K_RETURN):
                        self._confirm_choice()
                continue

            # 通常モード：クリックまたはスペースキーで進行
            is_click = ev.type == pygame.MOUSEBUTTONDOWN
            is_space = ev.type == pygame.KEYDOWN and (
                ev.key == pygame.K_SPACE
                or ev.key == pygame.K_z
                or ev.key == pygame.K_RETURN
            )

            if is_click or is_space:
                self._advance()

    def _get_cached_image(self, name, alpha=False):
        """画像をロードし、キャッシュから返す。名前が 'none' の場合は None を返す。"""
        if not name or name.lower() == "none":
            return None

        if name in self._image_cache:
            return self._image_cache[name]

        path = resource_path(os.path.join(self.base_dir, "img", name))
        if not os.path.isfile(path):
            print(f"VisualNovel: Resource not found - {path}")
            return None

        try:
            # ロード処理
            img = pygame.image.load(path)
            img = img.convert_alpha() if alpha else img.convert()

            # 背景の場合は画面サイズにリサイズ
            if not alpha:
                img = pygame.transform.scale(img, (VN_SCREEN_W, VN_SCREEN_H))

            self._image_cache[name] = img
            return img
        except Exception as e:
            print(f"VisualNovel: Error loading image {name} - {e}")
            return None

    def _load_current_scene(self):
        """現在のインデックスに基づき背景と立ち絵を更新する"""
        if self.index >= len(self.script):
            self.end_scene()
            return

        data = self.script[self.index]

        # アイテム付与
        reward = data.get("reward")
        if reward and hasattr(self.app, "items") and reward not in self.app.items:
            self.app.items.append(reward)
            print(f"VisualNovel: Item Get - {reward}")

        # 次の移動先マップが指定されている場合（ノベル終了後に遷移）
        next_map = data.get("next_map")
        if next_map:
            # next_map: {"map_id": "world", "x": 214, "y": 105}
            self.app.stop_map_transition = (
                next_map["map_id"],
                next_map.get("x"),
                next_map.get("y"),
            )

        # 背景の更新（指定がある場合のみ）
        bg_name = data.get("bg")
        if bg_name:
            # キャッシュ経由でロード
            img = self._get_cached_image(bg_name, alpha=False)
            if img:
                self.bg_image = img
            else:
                pass

        # 立ち絵の更新（指定がある場合のみ、"none" で消去）
        char_name = data.get("char")
        if char_name:
            if char_name.lower() == "none":
                self.char_image = None
            else:
                img = self._get_cached_image(char_name, alpha=True)
                if img:
                    # 指定されたスケール、または自動縮小
                    custom_scale = data.get("char_scale")

                    if custom_scale:
                        # JSONでスケール指定がある場合
                        w, h = img.get_size()
                        new_size = (int(w * custom_scale), int(h * custom_scale))
                        img = pygame.transform.smoothscale(img, new_size)

                        # オフセット指定（y座標調整用）
                        if "char_offset_y" in data:
                            self.char_offset_y = data["char_offset_y"]
                        else:
                            self.char_offset_y = 0
                    else:
                        # 自動調整: 画面高さの80%程度に収める
                        h_limit = int(VN_SCREEN_H * 0.8)
                        w, h = img.get_size()
                        if h > h_limit:
                            scale = h_limit / h
                            new_size = (int(w * scale), int(h * scale))
                            img = pygame.transform.smoothscale(img, new_size)
                        self.char_offset_y = 0

                    self.char_image = img

        # 背景立ち絵リセット（明示的な指定がない限りオフセットはリセットしない実装も可能だが、シーンごと描画なのでリセットが無難）
        # ただし char_name がない場合は char_image が更新されないので、
        # 前のシーンの画像が残る場合、オフセットも残すべきか？
        # 現状の実装は _load_current_scene で毎回 char_name をチェックしている。
        # char_nameがキーとして存在しない場合、何もしない（前の画像維持）仕様か？
        # -> はい。ただし今回は拡大縮小を伴うので、char_nameがない＝画像維持なら、オフセットも維持でOK。
        # char_nameがある場合のみ上記で char_offset_y を設定している。

        # 選択肢の確認
        choices = data.get("choices")
        if choices:
            self.waiting_for_choice = True
            self.choice_items = choices
            self.choice_index = 0
            self._setup_choice_layout()
        else:
            self.waiting_for_choice = False

    def _setup_choice_layout(self):
        """選択肢ボタンのレイアウト計算"""
        self.choice_rects = []
        if not self.choice_items:
            return

        count = len(self.choice_items)
        item_h = 60  # ボタンの高さ
        margin = 20  # ボタン間の余白
        total_h = count * item_h + (count - 1) * margin

        start_y = (VN_SCREEN_H - total_h) // 2
        btn_w = 600
        btn_x = (VN_SCREEN_W - btn_w) // 2

        for i in range(count):
            y = start_y + i * (item_h + margin)
            rect = pygame.Rect(btn_x, y, btn_w, item_h)
            self.choice_rects.append(rect)

    def _advance(self):
        """次のシーンへ進む（ジャンプまたはインクリメント）"""
        if self.index >= len(self.script):
            self.end_scene()
            return

        data = self.script[self.index]
        jump_to = data.get("jump_to")

        if jump_to and jump_to in self.labels:
            self.index = self.labels[jump_to]
        else:
            self.index += 1

        self._load_current_scene()

    def _confirm_choice(self):
        """選択肢決定時の処理"""
        data = self.script[self.index]
        correct_idx = data.get("answer")

        next_label = None

        # 正解/不正解による分岐
        if correct_idx is not None:
            if self.choice_index == correct_idx:
                next_label = data.get("jump_correct")
            else:
                next_label = data.get("jump_wrong")
        else:
            pass

        self.waiting_for_choice = False

        # 分岐先へジャンプ、なければ次へ
        if next_label and next_label in self.labels:
            self.index = self.labels[next_label]
        else:
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
            rect.y += self.char_offset_y  # オフセット適用
            screen.blit(self.char_image, rect)

        # 3. テキストウィンドウ
        self._draw_text_window(screen)

        # 4. 選択肢ウィンドウ
        if self.waiting_for_choice:
            self._draw_choices(screen)

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

    def _draw_choices(self, screen):
        """選択肢ウィンドウの描画（ボタン風）"""
        if not self.choice_items or not self.choice_rects:
            return

        # 背景（全体を少し暗くする）
        overlay = pygame.Surface((VN_SCREEN_W, VN_SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        for i, item in enumerate(self.choice_items):
            rect = self.choice_rects[i]
            is_selected = i == self.choice_index

            # 色設定
            if is_selected:
                bg_color = (60, 120, 180, 230)  # 青っぽくハイライト
                border_color = (255, 255, 200)
                text_color = (255, 255, 255)
            else:
                bg_color = (40, 40, 60, 200)  # 通常暗色
                border_color = (150, 150, 150)
                text_color = (200, 200, 200)

            # ボタン背景
            btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            btn_surf.fill(bg_color)
            screen.blit(btn_surf, rect.topleft)

            # 枠線
            pygame.draw.rect(screen, border_color, rect, 3 if is_selected else 2)

            # テキスト描画
            text = item.get("text", "") if isinstance(item, dict) else str(item)
            text_surf = self.ui_font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

            # 選択中の矢印
            if is_selected:
                cursor_char = "▶"
                cursor_surf = self.ui_font.render(cursor_char, True, border_color)
                screen.blit(
                    cursor_surf,
                    (rect.left + 20, rect.centery - cursor_surf.get_height() // 2),
                )

    def end_scene(self):
        """ノベルパートを終了し、RPGパートへ遷移する"""
        self.active = False
        self.app.start_rpg_game()
