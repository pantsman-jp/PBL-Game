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
        dialogues_path = resource_path(
            os.path.join("assets", "dialogues", "dialogues.json")
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
        if self.wait_frames > 0:
            self.wait_frames -= 1
        if not self.is_active():
            return
        if self.wait_frames > 0:
            return
        if keys.get("q"):
            self._close_dialog()
            return
        if self.quiz_mode and self.current_quiz:
            self._handle_quiz(keys)
            return
        if keys.get("z"):
            self.line_index += 1
            if self.line_index >= len(self.window_lines):
                self._advance_or_terminate()

    def _advance_or_terminate(self):
        npc_data = self.dialogues.get(self.active, {})
        quiz = npc_data.get("quiz")
        if quiz and not npc_data.get("quiz_done"):
            self.window_lines = []
            self.current_quiz = quiz
            self.quiz_mode = True
            self.quiz_choice = 0
            self.wait_frames = 15
            return
        self._process_npc_reward()
        self._check_novel_trigger()
        self._close_dialog()

    def _process_npc_reward(self):
        npc_data = self.dialogues.get(self.active, {})
        reward = npc_data.get("reward")
        if reward:
            self.app.items.extend(reward)
            del npc_data["reward"]

    def _check_novel_trigger(self):
        npc_data = self.dialogues.get(self.active, {})
        novel_trigger = npc_data.get("novel_trigger")
        if novel_trigger:
            self.app.scene_state = 2
            self.app.vn.start(novel_trigger)

    def _close_dialog(self):
        self.window_lines = []
        self.active = None
        self.line_index = 0
        self.current_quiz = None
        self.quiz_mode = False
        self.quiz_choice = 0
        self.wait_frames = 20

    def draw(self, screen, font):
        sw, sh = screen.get_size()
        ww, wh = sw * 0.8, sh * 0.3
        wx, wy = (sw - ww) // 2, sh - wh - 20
        rect = (wx, wy, ww, wh)
        if self.quiz_mode and self.current_quiz:
            q = self.current_quiz
            lines = [q.get("question", "")] + [
                f"{'>' if i == self.quiz_choice else ' '} {i + 1}. {c}"
                for i, c in enumerate(q.get("choices", []))
            ]
            draw_window(screen, font, lines, rect)
            return
        if self.window_lines:
            idx = min(self.line_index, len(self.window_lines) - 1)
            draw_window(screen, font, [self.window_lines[idx]], rect)

    def try_talk(self):
        if self.is_active() or self.wait_frames > 0:
            return
        px, py = self.app.x, self.app.y
        for key, data in self.dialogues.items():
            pos = data.get("position")
            if pos and abs(pos[0] - px) + abs(pos[1] - py) == 1:
                self.active = key
                self.open_dialog(data)
                return

    def open_dialog(self, data):
        self.window_lines = data.get("lines", [])
        self.line_index = 0
        self.current_quiz = None
        self.quiz_mode = False
        self.quiz_choice = 0
        self.wait_frames = 15

    def is_active(self):
        return self.active is not None

    def _handle_quiz(self, keys):
        q = self.current_quiz
        choices = q.get("choices", [])
        if keys.get("up"):
            self.quiz_choice = (self.quiz_choice - 1) % len(choices)
        elif keys.get("down"):
            self.quiz_choice = (self.quiz_choice + 1) % len(choices)
        elif keys.get("z"):
            npc_data = self.dialogues.get(self.active, {})
            if self.quiz_choice == q.get("answer", 0):
                reward = q.get("reward")
                if reward:
                    self.app.items.extend(reward)
                npc_data["quiz_done"] = True
            self._close_dialog()
