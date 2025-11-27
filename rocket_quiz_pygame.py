# rocket_quiz_pygame.py
# -*- coding: utf-8 -*-
"""
クイズでつくるロケット！～九工大生の挑戦～

画面構成:
 1. タイトル（オープニングテキスト）
 2. キャンパス（チュートリアル）
 3. 世界地図（各国へ移動）
 4. 各国ステージ（単色背景＋NPC＋クイズ）
 5. 全素材揃えて日本に戻るとロケット完成エンディング

操作:
  矢印キー: 移動
  Z / Enter / Space: 決定・話す・送り
  I: インベントリ表示 ON/OFF
  ESC: 終了
"""

import json
from typing import List, Optional, Tuple

import pygame

from sprites import draw_sprite  # 8x8ドット絵表示用（既存のものを利用）


# ================== グローバル設定（実サイズは起動時に決定） ==================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

SCALE = 4
PLAYER_SPEED = 220  # px/sec
NEAR_DIST = 48  # 会話判定距離

BG_COLOR = (10, 12, 24)
WINDOW_BG = (0, 0, 0)
WINDOW_BORDER = (200, 200, 200)
TEXT_COLOR = (240, 240, 240)
HINT_COLOR = (220, 220, 80)
ITEM_COLOR = (160, 220, 180)


# ================== ユーティリティ ==================


def wrap_text(text: str, width_chars: int) -> List[str]:
    """
    日本語・英語混在用の簡易折り返し。
    ・改行は維持
    ・スペースあり行は単語単位
    ・それ以外は指定文字数で分割
    """
    lines: List[str] = []

    for raw in text.split("\n"):
        if raw == "":
            lines.append("")
            continue

        if " " in raw:
            words = raw.split(" ")
            cur = ""
            for w in words:
                add = w if cur == "" else " " + w
                if len(cur) + len(add) <= width_chars:
                    cur += add
                else:
                    if cur:
                        lines.append(cur)
                    while len(w) > width_chars:
                        lines.append(w[:width_chars])
                        w = w[width_chars:]
                    cur = w
            if cur:
                lines.append(cur)
        else:
            cur = ""
            for ch in raw:
                cur += ch
                if len(cur) >= width_chars:
                    lines.append(cur)
                    cur = ""
            if cur:
                lines.append(cur)
    return lines


def dist2(x1: float, y1: float, x2: float, y2: float) -> float:
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy


# ================== 会話・クイズクラス ==================


class DialogLine:
    """会話1行分（誰が / 何を喋るか）"""

    def __init__(self, speaker: str, text: str) -> None:
        self.speaker = speaker
        self.text = text


class DialogPlayer:
    """
    会話ウィンドウ制御
    - 指定行を順番に表示
    - 1文字ずつ表示
    - Z/Enter/Spaceで送り
    """

    def __init__(
        self, lines: List[DialogLine], width_chars: int = 40, cps: float = 50.0
    ) -> None:
        expanded: List[str] = []

        for ln in lines:
            if ln.speaker:
                prefix = f"{ln.speaker}「"
                body = ln.text + "」"
            else:
                prefix = ""
                body = ln.text
            wrapped = wrap_text(body, max(1, width_chars - len(prefix)))
            if wrapped:
                expanded.append(prefix + wrapped[0])
                for w in wrapped[1:]:
                    expanded.append((" " * len(prefix)) + w)
            else:
                expanded.append(prefix + body)

        self.lines = expanded
        self.cps = cps
        self.index = 0
        self.char_progress = 0.0
        self.done = False

    def update(self, dt: float, confirm: bool) -> None:
        if self.done:
            return

        if self.index >= len(self.lines):
            self.done = True
            return

        self.char_progress += self.cps * dt

        if confirm:
            cur = self.lines[self.index]
            if self.char_progress < len(cur):
                self.char_progress = len(cur)
            else:
                self.index += 1
                self.char_progress = 0.0
                if self.index >= len(self.lines):
                    self.done = True

    def draw(self, game, x: int, y: int, w: int, h: int, title: str = "会話") -> None:
        game.draw_window(x, y, w, h, title)
        visible: List[str] = []
        start = max(0, self.index - 4)

        for i in range(start, self.index):
            visible.append(self.lines[i])

        if not self.done and self.index < len(self.lines):
            full = self.lines[self.index]
            n = int(max(0, min(len(full), self.char_progress)))
            visible.append(full[:n])

        yy = y + 26
        for line in visible[-5:]:
            game.draw_text(line, x + 14, yy, TEXT_COLOR)
            yy += 22


class Quiz:
    """クイズ内容"""

    def __init__(
        self,
        question: str,
        choices: List[str],
        answer_index: int,
        hint: str,
        after_success: List[DialogLine],
        after_fail: List[DialogLine],
    ) -> None:
        self.question = question
        self.choices = choices
        self.answer_index = answer_index
        self.hint = hint
        self.after_success = after_success
        self.after_fail = after_fail


class QuizPlayer:
    """
    クイズUI（選択式）
    - ↑↓で選択
    - Z/Enter/Spaceで決定
    """

    def __init__(self, quiz: Quiz, width_chars: int = 48) -> None:
        self.quiz = quiz
        self.selected = 0
        self.result: Optional[bool] = None
        self.show_hint = False
        self.question_lines = wrap_text(quiz.question, width_chars)

    def update(self, up_pressed: bool, down_pressed: bool, confirm: bool) -> None:
        if self.result is not None:
            return

        if up_pressed:
            self.selected = (self.selected - 1) % len(self.quiz.choices)
        if down_pressed:
            self.selected = (self.selected + 1) % len(self.quiz.choices)

        if confirm:
            self.result = self.selected == self.quiz.answer_index
            self.show_hint = not self.result

    def draw(self, game, x: int, y: int, w: int, h: int) -> None:
        game.draw_window(x, y, w, h, "クイズ")
        yy = y + 26
        for ln in self.question_lines:
            game.draw_text(ln, x + 14, yy, TEXT_COLOR)
            yy += 22

        yy += 4
        for i, choice in enumerate(self.quiz.choices):
            prefix = "▶" if i == self.selected else "  "
            color = HINT_COLOR if i == self.selected else TEXT_COLOR
            game.draw_text(f"{prefix}{i + 1}. {choice}", x + 14, yy, color)
            yy += 22

        if self.show_hint and self.result is False:
            game.draw_text(f"ヒント：{self.quiz.hint}", x + 14, y + h - 28, HINT_COLOR)


# ================== インベントリ ==================


class Inventory:
    """
    プレイヤーの持ち物。
    - Iキーで表示ON/OFF（Game側）
    - 表示時はプレイヤーの近くに追従
    """

    def __init__(self) -> None:
        self.items: List[str] = []

    def add(self, name: str) -> None:
        if name not in self.items:
            self.items.append(name)

    def has(self, name: str) -> bool:
        return name in self.items

    def has_all(self, names: List[str]) -> bool:
        return all(n in self.items for n in names)

    def clear(self) -> None:
        self.items.clear()

    def draw_following(self, game, player_x: float, player_y: float) -> None:
        w, h = 260, 140
        x = int(player_x + 40)
        y = int(player_y - h - 24)

        # 画面外補正
        if x + w > SCREEN_WIDTH - 16:
            x = SCREEN_WIDTH - w - 16
        if x < 16:
            x = 16
        if y < 16:
            y = 16
        if y + h > SCREEN_HEIGHT - 16:
            y = SCREEN_HEIGHT - h - 16

        game.draw_window(x, y, w, h, "持ち物 [I]")
        yy = y + 30
        if not self.items:
            game.draw_text("なし", x + 14, yy, (160, 160, 160))
        else:
            for it in self.items[-6:]:
                game.draw_text(f"- {it}", x + 14, yy, ITEM_COLOR)
                yy += 22


# ================== プレイヤー ==================


class Player:
    def __init__(self, x: int, y: int) -> None:
        self.x = float(x)
        self.y = float(y)

    def set_pos(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def update(self, keys, dt: float) -> None:
        dx = dy = 0.0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1

        if dx or dy:
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length
            self.x += dx * PLAYER_SPEED * dt
            self.y += dy * PLAYER_SPEED * dt

        # 画面内に制限
        margin = 32
        self.x = max(margin, min(SCREEN_WIDTH - margin, self.x))
        self.y = max(margin, min(SCREEN_HEIGHT - margin, self.y))

    def draw(self, screen: pygame.Surface) -> None:
        # 主人公：kyukodaiスプライト
        draw_sprite(screen, "kyukodai", int(self.x - 16), int(self.y - 16), SCALE)


# ================== 国シーン ==================


class CountryScene:
    """
    各国の情報（世界地図上の位置＋会話＋クイズ＋報酬）
    """

    def __init__(
        self,
        scene_id: str,
        name: str,
        npc: str,
        sprite_key: str,
        pos_ratio: Tuple[float, float],
        pre_dialog: List[DialogLine],
        quiz: Quiz,
        reward: str,
    ) -> None:
        self.id = scene_id
        self.name = name
        self.npc_name = npc
        self.sprite_key = sprite_key
        self.rx, self.ry = pos_ratio
        self.pre_dialog = pre_dialog
        self.quiz = quiz
        self.reward = reward
        self.cleared = False

    def world_pos(self) -> Tuple[float, float]:
        return self.rx * SCREEN_WIDTH, self.ry * SCREEN_HEIGHT


# ================== Game本体 ==================


class Game:
    def __init__(self, scenario_path: str) -> None:
        pygame.init()

        # フルスクリーンで起動
        info = pygame.display.Info()
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
        )
        pygame.display.set_caption("クイズでつくるロケット！～九工大生の挑戦～")
        self.clock = pygame.time.Clock()

        # 日本語フォント優先
        font_name = pygame.font.match_font(
            [
                "meiryo",
                "Yu Gothic",
                "MS Gothic",
                "Noto Sans CJK JP",
                "msgothic",
                "consolas",
            ]
        )
        self.font = (
            pygame.font.Font(font_name, 24)
            if font_name
            else pygame.font.SysFont(None, 24)
        )

        # 背景：world_map.png（なければ簡易世界地図）
        self.world_map = self._load_world_map()

        # ストーリー&状態
        self.screen_state = "title"  # title / campus / worldmap / country / end
        self.mode = (
            "free"  # free / dialog / quiz / after（campus/worldmap/countryで使用）
        )

        # タイトル用テキスト
        self.title_lines = [
            "かつて……この国には、宇宙を夢見る者たちがいた。",
            "しかし、時は流れ、夢は「無理だ」の一言で押しつぶされた。",
            "それでも、一人の学生がいた――九州工業大学。",
            "「みんなで力を合わせれば、もう一度ロケットを飛ばせるはずだ！」",
            "クイズでつくるロケット！～九工大生の挑戦～",
        ]
        self.title_index = 0

        # プレイヤー
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # インベントリ
        self.inventory = Inventory()
        self.inventory_visible = True

        # シナリオ読み込み（各国）
        self.countries: List[CountryScene] = self._load_countries(scenario_path)

        # キャンパス関連フラグ
        self.tutorial_done = False
        self.spoke_prof = False
        self.rocket_acquired = False
        self.return_from_world = False

        # 会話・クイズ一時オブジェクト
        self.dialog_player: Optional[DialogPlayer] = None
        self.dialog_context: str = ""
        self.quiz_player: Optional[QuizPlayer] = None
        self.quiz_context: str = ""
        self.after_dialog: Optional[DialogPlayer] = None

        # 現在いる国
        self.active_country: Optional[CountryScene] = None

    # ---------- 共通描画ヘルパ ----------

    def draw_text(self, text: str, x: int, y: int, color=TEXT_COLOR) -> None:
        surf = self.font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def draw_window(
        self, x: int, y: int, w: int, h: int, title: Optional[str] = None
    ) -> None:
        pygame.draw.rect(self.screen, WINDOW_BORDER, (x, y, w, h), 2)
        pygame.draw.rect(self.screen, WINDOW_BG, (x + 2, y + 26, w - 4, h - 28))
        if title:
            self.draw_text(title, x + 8, y + 4, HINT_COLOR)

    # ---------- world_map読み込み / フォールバック ----------

    def _load_world_map(self) -> Optional[pygame.Surface]:
        try:
            img = pygame.image.load("world_map.png").convert()
            return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            return None

    def _draw_fallback_world_map(self) -> None:
        # 超ざっくり世界地図
        self.screen.fill((8, 16, 40))

        def cont(color, rect):
            pygame.draw.ellipse(self.screen, color, rect)

        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        cont((40, 100, 40), (w * 0.05, h * 0.20, w * 0.25, h * 0.30))  # 北米
        cont((40, 120, 40), (w * 0.18, h * 0.45, w * 0.25, h * 0.35))  # 南米
        cont((60, 130, 50), (w * 0.42, h * 0.22, w * 0.18, h * 0.25))  # 欧州
        cont((40, 130, 50), (w * 0.44, h * 0.40, w * 0.22, h * 0.32))  # アフリカ
        cont((40, 150, 60), (w * 0.60, h * 0.25, w * 0.30, h * 0.40))  # アジア
        cont((40, 160, 80), (w * 0.78, h * 0.60, w * 0.18, h * 0.22))  # オセアニア

    # ---------- scenario.json 読み込み ----------

    def _load_countries(self, path: str) -> List[CountryScene]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        result: List[CountryScene] = []
        for s in data["scenes"]:
            scene_id = s["id"]
            name = s["name"]
            npc = s["npc"]
            sprite_key = s.get("sprite", "")
            rx, ry = s["position"]

            pre_dialog = [DialogLine(d["speaker"], d["text"]) for d in s["pre_dialog"]]
            q = s["quiz"]
            quiz = Quiz(
                question=q["question"],
                choices=q["choices"],
                answer_index=q["answer_index"],
                hint=q["hint"],
                after_success=[
                    DialogLine(d["speaker"], d["text"]) for d in q["after_success"]
                ],
                after_fail=[
                    DialogLine(d["speaker"], d["text"]) for d in q["after_fail"]
                ],
            )
            reward = s.get("reward", "")

            result.append(
                CountryScene(
                    scene_id=scene_id,
                    name=name,
                    npc=npc,
                    sprite_key=sprite_key,
                    pos_ratio=(rx, ry),
                    pre_dialog=pre_dialog,
                    quiz=quiz,
                    reward=reward,
                )
            )
        return result

    # ---------- メインループ ----------

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            confirm = False
            up_pressed = False
            down_pressed = False
            toggle_inv = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                        confirm = True
                    if event.key == pygame.K_UP:
                        up_pressed = True
                    if event.key == pygame.K_DOWN:
                        down_pressed = True
                    if event.key == pygame.K_i:
                        toggle_inv = True

            keys = pygame.key.get_pressed()
            if toggle_inv:
                self.inventory_visible = not self.inventory_visible

            # 状態別アップデート
            if self.screen_state == "title":
                self.update_title(confirm)
            elif self.screen_state == "campus":
                self.update_campus(dt, keys, confirm, up_pressed, down_pressed)
            elif self.screen_state == "worldmap":
                self.update_worldmap(dt, keys, confirm)
            elif self.screen_state == "country":
                self.update_country(dt, confirm, up_pressed, down_pressed)
            elif self.screen_state == "end":
                # エンディング画面：ESCで終了のみ
                pass

            # 描画
            self.draw()
            pygame.display.flip()

        pygame.quit()

    # ================== 各画面の更新処理 ==================

    # --- 1. タイトル画面 ---

    def update_title(self, confirm: bool) -> None:
        if confirm:
            self.title_index += 1
            if self.title_index >= len(self.title_lines):
                # キャンパスへ
                self.enter_campus(first=True)

    # --- 2. キャンパス画面（チュートリアル＋最終エンド） ---

    def enter_campus(self, first: bool = False) -> None:
        self.screen_state = "campus"
        self.mode = "free"
        # 初回 or 帰還時とも、とりあえず中央付近に出す
        self.player.set_pos(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.7)
        if not first:
            self.return_from_world = True

    def _campus_positions(self):
        # ハカセ・ミカ・ロボ助の立ち位置
        prof = (SCREEN_WIDTH * 0.3, SCREEN_HEIGHT * 0.55)
        mika = (SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.55)
        robo = (SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.55)
        gate_top = (SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.12)
        return prof, mika, robo, gate_top

    def update_campus(
        self, dt: float, keys, confirm: bool, up_pressed: bool, down_pressed: bool
    ) -> None:
        prof_pos, mika_pos, robo_pos, gate_pos = self._campus_positions()

        # 会話/クイズ中
        if self.mode == "dialog":
            self.dialog_player.update(dt, confirm)
            if self.dialog_player.done and confirm:
                if self.dialog_context == "prof_intro":
                    self.spoke_prof = True
                    self.mode = "free"
                    self.dialog_player = None
                elif self.dialog_context == "final_exchange":
                    # 素材と交換してロケット完成 → エピローグへ
                    self.inventory.clear()
                    self.inventory.add("完成ロケット")
                    self.rocket_acquired = True
                    self.start_epilogue()
                else:
                    self.mode = "free"
                    self.dialog_player = None
            return

        if self.mode == "quiz":
            # チュートリアルクイズのみ
            self.quiz_player.update(up_pressed, down_pressed, confirm)
            if self.quiz_player.result is not None:
                lines = (
                    self.quiz_player.quiz.after_success
                    if self.quiz_player.result
                    else self.quiz_player.quiz.after_fail
                )
                self.after_dialog = DialogPlayer(lines)
                self.mode = "after"
            return

        if self.mode == "after":
            self.after_dialog.update(dt, confirm)
            if self.after_dialog.done and confirm:
                if self.quiz_context == "tutorial" and self.quiz_player.result:
                    self.tutorial_done = True
                # リセットして自由行動へ
                self.quiz_player = None
                self.after_dialog = None
                self.quiz_context = ""
                self.mode = "free"
            return

        # 自由行動
        self.player.update(keys, dt)

        if not confirm:
            return

        px, py = self.player.x, self.player.y

        # ハカセ教授と会話
        if dist2(px, py, *prof_pos) <= NEAR_DIST * NEAR_DIST:
            if not self.spoke_prof:
                # 導入
                lines = [
                    DialogLine(
                        "ハカセ", "おお、九工大生よ。ロケットを作りたいそうじゃな？"
                    ),
                    DialogLine("九工大生", "はい！ 世界に挑戦したいんです！"),
                    DialogLine(
                        "ハカセ", "ならば世界を巡り、知恵と素材をクイズで集めるのじゃ。"
                    ),
                    DialogLine(
                        "ハカセ",
                        "まずはロボ助に操作を教わるのだ。あやつは優秀な教師でな。",
                    ),
                ]
                self.dialog_player = DialogPlayer(lines)
                self.dialog_context = "prof_intro"
                self.mode = "dialog"
            else:
                # チュートリアル済 or 帰還後
                if self.rocket_acquired:
                    # すでにロケット完成後は簡単な一言
                    lines = [
                        DialogLine(
                            "ハカセ", "ロケットはもう完成した。次の夢を見つけるのじゃ。"
                        )
                    ]
                    self.dialog_player = DialogPlayer(lines)
                    self.dialog_context = "misc"
                    self.mode = "dialog"
                else:
                    # 素材揃っていれば最終イベント
                    required = [
                        "天然ゴムブロック",
                        "超合金プレート",
                        "液体燃料タンク",
                        "アルミニウムインゴット",
                        "制御プログラムチップ",
                    ]
                    if self.inventory.has_all(required):
                        lines = [
                            DialogLine(
                                "ミカ先輩",
                                "九工大生！ 世界中を回って全部集めてきたんだね！",
                            ),
                            DialogLine(
                                "ハカセ", "見事じゃ。この素材とプログラムがあれば……"
                            ),
                            DialogLine(
                                "ハカセ",
                                "ついにロケットを完成させられる！ さあ、託してくれ。",
                            ),
                        ]
                        self.dialog_player = DialogPlayer(lines)
                        self.dialog_context = "final_exchange"
                        self.mode = "dialog"
                    else:
                        lines = [
                            DialogLine("ハカセ", "素材はまだ足りんようじゃ。"),
                            DialogLine(
                                "ハカセ",
                                "世界地図から各地へ飛び、クイズで素材を集めてくるのだ。",
                            ),
                        ]
                        self.dialog_player = DialogPlayer(lines)
                        self.dialog_context = "misc"
                        self.mode = "dialog"
            return

        # ロボ助（チュートリアルクイズ）
        if dist2(px, py, *robo_pos) <= NEAR_DIST * NEAR_DIST:
            if not self.spoke_prof:
                lines = [DialogLine("ロボ助", "まずはハカセ教授に話しかけるロボ。")]
                self.dialog_player = DialogPlayer(lines)
                self.dialog_context = "misc"
                self.mode = "dialog"
            elif not self.tutorial_done:
                q = Quiz(
                    question="君は“宇宙システム工学科”に入りたいか？",
                    choices=["はい", "いいえ"],
                    answer_index=0,
                    hint="ここで“いいえ”を選ぶと話が進まない気がする。",
                    after_success=[
                        DialogLine("ロボ助", "その意気ロボ！ 操作方法を教えるロボ！"),
                        DialogLine(
                            "ロボ助", "矢印キーで移動、Z/Enter/Spaceで会話と決定ロボ。"
                        ),
                        DialogLine(
                            "ロボ助", "世界地図で各国の仲間とクイズに挑むロボ！"
                        ),
                    ],
                    after_fail=[
                        DialogLine(
                            "ロボ助",
                            "本当ロボか？ ロケット作りたくないロボ？ もう一度考えるロボ。",
                        )
                    ],
                )
                self.quiz_player = QuizPlayer(q)
                self.quiz_context = "tutorial"
                self.mode = "quiz"
            else:
                lines = [
                    DialogLine("ロボ助", "準備万端ロボ！ 世界地図で素材を集めるロボ！")
                ]
                self.dialog_player = DialogPlayer(lines)
                self.dialog_context = "misc"
                self.mode = "dialog"
            return

        # ミカ先輩（フレーバー）
        if dist2(px, py, *mika_pos) <= NEAR_DIST * NEAR_DIST:
            lines = [
                DialogLine("ミカ先輩", "困ったら私に話しかけてね。応援してるから！")
            ]
            self.dialog_player = DialogPlayer(lines)
            self.dialog_context = "misc"
            self.mode = "dialog"
            return

        # 上部ゲートから世界地図へ（チュートリアル完了後のみ）
        if self.tutorial_done and py < SCREEN_HEIGHT * 0.18:
            self.enter_worldmap()
            return

    # --- 3. 世界地図画面 ---

    def enter_worldmap(self) -> None:
        self.screen_state = "worldmap"
        self.mode = "free"
        # 日本付近に配置
        self.player.set_pos(SCREEN_WIDTH * 0.25, SCREEN_HEIGHT * 0.35)
        self.return_from_world = False

    def _find_near_country_on_map(self) -> Optional[CountryScene]:
        for c in self.countries:
            x, y = c.world_pos()
            if dist2(self.player.x, self.player.y, x, y) <= (NEAR_DIST * 1.4) ** 2:
                return c
        return None

    def _near_kyutech_gate_on_map(self) -> bool:
        # 日本(九工大)あたり：左上寄りの基準
        gx, gy = SCREEN_WIDTH * 0.20, SCREEN_HEIGHT * 0.32
        return dist2(self.player.x, self.player.y, gx, gy) <= (NEAR_DIST * 1.6) ** 2

    def update_worldmap(self, dt: float, keys, confirm: bool) -> None:
        if self.mode == "dialog":
            self.dialog_player.update(dt, confirm)
            if self.dialog_player.done and confirm:
                self.mode = "free"
                self.dialog_player = None
            return

        # worldmapではクイズはしない（国に入ってから）
        if self.mode != "free":
            return

        self.player.update(keys, dt)

        if not confirm:
            return

        # 日本に戻る（キャンパスへ）
        if self._near_kyutech_gate_on_map():
            self.enter_campus(first=False)
            return

        # 各国の入口
        country = self._find_near_country_on_map()
        if not country:
            return

        # 入場条件チェック
        # オーストラリア：乗船許可証必須
        if country.id == "australia" and not self.inventory.has("乗船許可証"):
            lines = [
                DialogLine("システム", "まだ自力でオーストラリアへは渡れない。"),
                DialogLine("システム", "アフリカの港町で船乗りカイに会おう。"),
            ]
            self.dialog_player = DialogPlayer(lines)
            self.mode = "dialog"
            return

        # インド：主要4素材が必要
        if country.id == "india_final":
            required_pre = [
                "天然ゴムブロック",
                "超合金プレート",
                "液体燃料タンク",
                "アルミニウムインゴット",
            ]
            if not self.inventory.has_all(required_pre):
                lines = [
                    DialogLine("システム", "まだ集めきれていない素材がある。"),
                    DialogLine(
                        "システム", "ゴム・合金・燃料・アルミを集めてから来よう。"
                    ),
                ]
                self.dialog_player = DialogPlayer(lines)
                self.mode = "dialog"
                return

        # 条件OK → 国ステージへ
        self.enter_country(country)

    # --- 4. 各国ステージ ---

    def enter_country(self, country: CountryScene) -> None:
        self.screen_state = "country"
        self.mode = "dialog"
        self.active_country = country
        # プレイヤーは下側中央に立たせる
        self.player.set_pos(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.75)
        # 入場時の導入会話
        self.dialog_player = DialogPlayer(country.pre_dialog)
        self.dialog_context = "country_pre"

    def _country_bg_color(self, cid: str) -> Tuple[int, int, int]:
        if cid == "brazil":
            return (8, 70, 40)
        if cid == "africa_port":
            return (40, 40, 80)
        if cid == "germany":
            return (30, 30, 60)
        if cid == "russia":
            return (60, 60, 90)
        if cid == "australia":
            return (90, 70, 40)
        if cid == "india_final":
            return (60, 30, 70)
        return (20, 20, 40)

    def update_country(
        self, dt: float, confirm: bool, up_pressed: bool, down_pressed: bool
    ) -> None:
        c = self.active_country
        if c is None:
            # 安全策：ワールドマップに戻す
            self.enter_worldmap()
            return

        if self.mode == "dialog":
            self.dialog_player.update(dt, confirm)
            if self.dialog_player.done and confirm:
                if self.dialog_context == "country_pre":
                    if c.cleared:
                        # クリア済なら挨拶だけして地図へ戻る
                        self.enter_worldmap()
                    else:
                        # クイズ開始
                        self.quiz_player = QuizPlayer(c.quiz)
                        self.quiz_context = "country"
                        self.mode = "quiz"
                else:
                    # その他会話終了時
                    self.mode = "free"
                    self.dialog_player = None
            return

        if self.mode == "quiz":
            self.quiz_player.update(up_pressed, down_pressed, confirm)
            if self.quiz_player.result is not None:
                # 結果に応じた会話
                if self.quiz_player.result:
                    c.cleared = True
                    if c.reward:
                        self.inventory.add(c.reward)
                    lines = c.quiz.after_success
                else:
                    lines = c.quiz.after_fail
                self.after_dialog = DialogPlayer(lines)
                self.mode = "after"
            return

        if self.mode == "after":
            self.after_dialog.update(dt, confirm)
            if self.after_dialog.done and confirm:
                if self.quiz_player.result:
                    # 正解後 → ワールドマップに戻る
                    self.quiz_player = None
                    self.after_dialog = None
                    self.active_country = None
                    self.quiz_context = ""
                    self.enter_worldmap()
                else:
                    # 不正解 → 同じ国で再挑戦
                    self.quiz_player = QuizPlayer(c.quiz)
                    self.after_dialog = None
                    self.mode = "quiz"
            return

        # mode == "free" になったら、Zでマップに戻れるようにしておく（保険）
        if confirm:
            self.enter_worldmap()

    # --- 5. エピローグ（ロケット完成後） ---

    def start_epilogue(self) -> None:
        self.screen_state = "end"
        ep_lines = [
            DialogLine("", "すべての素材と知恵が、一つのロケットに組み上がっていく……"),
            DialogLine("ミカ先輩", "九工大生！ 本当に、やり遂げたんだね。"),
            DialogLine("ハカセ", "点火シーケンス、スタート！"),
            DialogLine("", "ゴオォォォ……"),
            DialogLine("", "ロケットは夜空を切り裂き、星々の彼方へと飛び立っていく。"),
            DialogLine("", "知恵は、世界をつなぐ燃料だ。"),
        ]
        self.dialog_player = DialogPlayer(ep_lines)
        self.mode = "dialog"

    # ================== 各画面の描画 ==================

    def draw(self) -> None:
        if self.screen_state == "title":
            self.draw_title()
        elif self.screen_state == "campus":
            self.draw_campus()
        elif self.screen_state == "worldmap":
            self.draw_worldmap()
        elif self.screen_state == "country":
            self.draw_country()
        elif self.screen_state == "end":
            self.draw_end()

    # --- タイトル描画 ---

    def draw_title(self) -> None:
        self.screen.fill((0, 0, 0))
        max_i = min(self.title_index + 1, len(self.title_lines))
        y = SCREEN_HEIGHT * 0.3
        for i in range(max_i):
            line = self.title_lines[i]
            color = TEXT_COLOR if i < len(self.title_lines) - 1 else HINT_COLOR
            surf = self.font.render(line, True, color)
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, int(y)))
            self.screen.blit(surf, rect)
            y += 40
        hint = "Z / Enter / Space で進む"
        hs = self.font.render(hint, True, (180, 180, 180))
        hr = hs.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.8)))
        self.screen.blit(hs, hr)

    # --- キャンパス描画 ---

    def draw_campus(self) -> None:
        self.screen.fill((16, 40, 60))

        prof_pos, mika_pos, robo_pos, gate_pos = self._campus_positions()

        # 校舎っぽい矩形
        pygame.draw.rect(
            self.screen,
            (20, 80, 110),
            (
                SCREEN_WIDTH * 0.15,
                SCREEN_HEIGHT * 0.35,
                SCREEN_WIDTH * 0.7,
                SCREEN_HEIGHT * 0.18,
            ),
        )

        # NPC（シンプルな矩形キャラ）
        def draw_npc_box(x, y, color, name):
            pygame.draw.rect(self.screen, color, (int(x - 18), int(y - 40), 36, 40))
            self.draw_text(name, int(x - 24), int(y - 52), TEXT_COLOR)

        draw_npc_box(*prof_pos, (220, 220, 120), "ハカセ")
        draw_npc_box(*mika_pos, (220, 150, 220), "ミカ")
        draw_npc_box(*robo_pos, (160, 220, 220), "ロボ助")

        # 上部ゲート
        pygame.draw.rect(
            self.screen,
            (240, 240, 240),
            (int(gate_pos[0] - 80), int(gate_pos[1] - 10), 160, 8),
        )
        self.draw_text(
            "世界地図へ", int(gate_pos[0] - 60), int(gate_pos[1] - 40), HINT_COLOR
        )

        # プレイヤー
        self.player.draw(self.screen)

        # ガイド
        self.draw_window(24, 24, 520, 64, "操作説明")
        self.draw_text(
            "矢印:移動  Z/Enter/Space:話す/決定  I:持ち物  ESC:終了", 40, 56, TEXT_COLOR
        )

        # 会話／クイズ表示
        if self.mode == "dialog" and self.dialog_player:
            self.dialog_player.draw(
                self, 40, SCREEN_HEIGHT - 220, SCREEN_WIDTH - 80, 200
            )
        elif self.mode == "quiz" and self.quiz_player:
            self.quiz_player.draw(self, 40, SCREEN_HEIGHT - 260, SCREEN_WIDTH - 80, 240)
        elif self.mode == "after" and self.after_dialog:
            self.after_dialog.draw(
                self, 40, SCREEN_HEIGHT - 220, SCREEN_WIDTH - 80, 200
            )

        # インベントリ
        if self.inventory_visible:
            self.inventory.draw_following(self, self.player.x, self.player.y)

    # --- 世界地図描画 ---

    def draw_worldmap(self) -> None:
        if self.world_map:
            self.screen.blit(self.world_map, (0, 0))
        else:
            self._draw_fallback_world_map()

        # 各国アイコン
        for c in self.countries:
            x, y = c.world_pos()
            if c.sprite_key:
                draw_sprite(self.screen, c.sprite_key, int(x - 16), int(y - 16), SCALE)
            else:
                pygame.draw.circle(self.screen, (250, 220, 120), (int(x), int(y)), 10)
            # クリア判定で縁取りなどしても良い（簡易に★表示）
            if c.cleared:
                self.draw_text("★", int(x + 10), int(y - 10), HINT_COLOR)

        # 日本（九工大）マーク
        jx, jy = SCREEN_WIDTH * 0.20, SCREEN_HEIGHT * 0.32
        pygame.draw.circle(self.screen, (255, 255, 255), (int(jx), int(jy)), 8)
        self.draw_text("九工大", int(jx - 24), int(jy - 28), (255, 255, 255))

        # プレイヤー
        self.player.draw(self.screen)

        # 説明
        self.draw_window(24, 24, 640, 64, "世界地図")
        self.draw_text(
            "各国のNPCに近づいて Z/Enter/Space で入国。九工大付近で押すと日本に戻る。",
            40,
            56,
            TEXT_COLOR,
        )

        # 会話
        if self.mode == "dialog" and self.dialog_player:
            self.dialog_player.draw(
                self, 40, SCREEN_HEIGHT - 220, SCREEN_WIDTH - 80, 200
            )

        # インベントリ
        if self.inventory_visible:
            self.inventory.draw_following(self, self.player.x, self.player.y)

    # --- 国ステージ描画 ---

    def draw_country(self) -> None:
        c = self.active_country
        if c is None:
            self.enter_worldmap()
            return

        self.screen.fill(self._country_bg_color(c.id))

        # 国名
        self.draw_window(24, 24, 420, 56, c.name)
        self.draw_text("Z/Enter/Space：会話/決定", 40, 56, TEXT_COLOR)

        # NPC
        npc_x = SCREEN_WIDTH * 0.5
        npc_y = SCREEN_HEIGHT * 0.45
        if c.sprite_key:
            draw_sprite(
                self.screen, c.sprite_key, int(npc_x - 16), int(npc_y - 24), SCALE
            )
        else:
            pygame.draw.rect(
                self.screen, (240, 200, 120), (int(npc_x - 18), int(npc_y - 40), 36, 40)
            )
        self.draw_text(c.npc_name, int(npc_x - 40), int(npc_y - 64), TEXT_COLOR)

        # プレイヤー
        self.player.draw(self.screen)

        # 会話／クイズ
        if self.mode == "dialog" and self.dialog_player:
            self.dialog_player.draw(
                self, 40, SCREEN_HEIGHT - 240, SCREEN_WIDTH - 80, 220
            )
        elif self.mode == "quiz" and self.quiz_player:
            self.quiz_player.draw(self, 40, SCREEN_HEIGHT - 260, SCREEN_WIDTH - 80, 240)
        elif self.mode == "after" and self.after_dialog:
            self.after_dialog.draw(
                self, 40, SCREEN_HEIGHT - 240, SCREEN_WIDTH - 80, 220
            )

        # インベントリ
        if self.inventory_visible:
            self.inventory.draw_following(self, self.player.x, self.player.y)

    # --- エンディング描画 ---

    def draw_end(self) -> None:
        self.screen.fill((0, 0, 0))
        if self.dialog_player and not self.dialog_player.done:
            self.dialog_player.draw(
                self, 80, SCREEN_HEIGHT - 260, SCREEN_WIDTH - 160, 240, "エピローグ"
            )
        else:
            msg1 = "ありがとう！ ロケットは星空へ飛び立った。"
            msg2 = "ESCキーで終了します。"
            s1 = self.font.render(msg1, True, TEXT_COLOR)
            s2 = self.font.render(msg2, True, (180, 180, 180))
            self.screen.blit(
                s1, s1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            )
            self.screen.blit(
                s2, s2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            )


# ================== エントリポイント ==================

if __name__ == "__main__":
    Game("scenario.json").run()
