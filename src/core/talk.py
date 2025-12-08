"""
会話・クイズ管理 | src/core/talk.py

dialogues.json を読み込み、Z で進行、Q で離脱、矢印で選択、正解で報酬を付与
"""

import os
from src.ui import draw_window
from src.utils import load_json, resource_path


class Talk:
    def __init__(self, app):
        self.app = app
        BASE_DIR = resource_path("assets")
        dialogues_path = resource_path(
            os.path.join(BASE_DIR, "dialogues", "dialogues.json")
        )
        self.dialogues = load_json(dialogues_path) or {}
        self.active = None
        self.window_lines = []
        self.line_index = 0
        self.current_quiz = None
        self.quiz_mode = False
        self.quiz_choice = 0
        self.wait_frames = 0

    def update(self, keys):
        """
        会話とクイズの状態更新
        keys: dict {"z": True/False, "q": True/False, "up": True/False, "down": True/False}
        """
        if not (self.window_lines or self.quiz_mode or self.current_quiz):
            return
        if self.wait_frames > 0:
            self.wait_frames -= 1
            return
        if keys.get("q"):
            self.window_lines = []
            self.current_quiz = None
            self.quiz_mode = False
            self.active = None
            return

        # --- クイズモード ---
        if self.quiz_mode and self.current_quiz:
            self._handle_quiz(keys)
            return

        # --- 通常会話モード ---
        if keys.get("z"):
            self.line_index += 1
            if self.line_index < len(self.window_lines):
                pass
            else:
                # 会話終了後、クイズ開始可能
                if self.current_quiz:
                    self.window_lines = []
                    self.quiz_mode = True
                    self.quiz_choice = 0
                    self.wait_frames = 10
                else:
                    self.window_lines = []
                    self.active = None

    def draw(self, screen, font):
        """
        会話ウィンドウの描画
        screen: pygame.Surface
        font: pygame.font.Font
        """
        # --- クイズ描画優先 ---
        if self.quiz_mode and self.current_quiz:
            q = self.current_quiz
            lines = [q.get("question", "")]
            for i, c in enumerate(q.get("choices", [])):
                prefix = ">" if i == self.quiz_choice else " "
                lines.append(f"{prefix} {i + 1}. {c}")
            draw_window(screen, font, lines)
            return

        # --- 通常会話描画 ---
        if self.window_lines:
            idx = min(self.line_index, max(0, len(self.window_lines) - 1))
            lines = [self.window_lines[idx]]
            draw_window(screen, font, lines)

    def try_talk(self):
        """
        プレイヤー位置の四近傍にいるNPCを探索して会話開始
        """
        px, py = self.app.x, self.app.y
        for key, data in self.dialogues.items():
            pos = data.get("position")
            if pos:
                nx, ny = pos[0], pos[1]
                if abs(nx - px) + abs(ny - py) == 1:  # 四近傍判定
                    self.active = key
                    self.open_dialog(data)
                    return

    def open_dialog(self, data):
        """
        会話開始処理
        data: NPCデータ（lines, quizなど）
        """
        self.window_lines = data.get("lines", [])
        self.line_index = 0
        self.current_quiz = data.get("quiz")
        self.quiz_mode = False
        self.quiz_choice = 0
        self.wait_frames = 10  # 押しっぱなし防止の待機フレーム

    def is_active(self):
        """
        会話中かどうか
        """
        return self.window_lines or self.quiz_mode

    def _handle_quiz(self, keys):
        """
        クイズの入力処理
        keys: dict
        """
        q = self.current_quiz
        if keys.get("up"):
            self.quiz_choice = (self.quiz_choice - 1) % len(q["choices"])
        elif keys.get("down"):
            self.quiz_choice = (self.quiz_choice + 1) % len(q["choices"])
        elif keys.get("z"):
            # 決定
            correct = q.get("answer", 0)
            if self.quiz_choice == correct:
                reward = q.get("reward")
                if reward and reward not in self.app.items:
                    self.app.items.append(reward)
                self.window_lines = ["Correct!", f"Reward: {reward}"]
            else:
                self.window_lines = ["Wrong.", f"Answer: {q['choices'][correct]}"]
            # クイズ終了
            self.current_quiz = None
            self.quiz_mode = False
            self.active = None
