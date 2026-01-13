"""
会話・クイズ管理 | src/core/talk.py
dialogues.json を読み込み、Z で進行、Q で離脱、矢印で選択、正解で報酬を付与
"""

import os
from src.ui import draw_window
from src.utils import load_json, resource_path


class Talk:
    """
    NPCとの会話、およびクイズシステムを制御するクラス
    """

    def __init__(self, app):
        self.app = app

        # リソースパスの構築とデータロード
        dialogues_path = resource_path(
            os.path.join("assets", "dialogues", "dialogues.json")
        )
        self.dialogues = load_json(dialogues_path) or {}

        # 会話状態管理
        self.active = None  # 現在会話中のNPCキー
        self.window_lines = []  # 表示中のテキスト行リスト
        self.line_index = 0  # 現在表示中のテキストのインデックス

        # クイズ状態管理
        self.quiz_mode = False
        self.current_quiz = None
        self.quiz_choice = 0  # 選択中の選択肢番号

        # 入力遅延用（連続入力の防止）
        self.wait_frames = 0

    # --- 更新処理 ---

    def update(self, keys):
        """毎フレームの更新処理"""
        # 待機カウントの更新
        if self.wait_frames > 0:
            self.wait_frames -= 1

        if not self.is_active() or self.wait_frames > 0:
            return

        # Qキーで会話を強制終了
        if keys.get("q"):
            self._close_dialog()
            return

        # モードに応じたイベントハンドリング
        if self.quiz_mode:
            self._handle_quiz(keys)
        else:
            self._handle_dialog(keys)

    def _handle_dialog(self, keys):
        """通常のテキスト送りの処理"""
        if keys.get("z"):
            self.line_index += 1

            # 全ての行を読み終えた場合
            if self.line_index >= len(self.window_lines):
                self._advance_to_next_state()

    def _advance_to_next_state(self):
        """テキスト終了後の遷移判定（クイズへ行くか、終了するか）"""
        npc_data = self.dialogues.get(self.active, {})
        quiz = npc_data.get("quiz")

        # 未達成のクイズがある場合はクイズモードへ
        if quiz and not npc_data.get("quiz_done"):
            self.quiz_mode = True
            self.current_quiz = quiz
            self.quiz_choice = 0
            self.window_lines = []
            self.wait_frames = 15
        else:
            # 終了処理
            self._finalize_conversation(npc_data)

    def _finalize_conversation(self, npc_data):
        """会話終了時の報酬付与とトリガー確認"""
        # 報酬の付与（一度きり）
        reward = npc_data.get("reward")
        if reward:
            self.app.items.extend(reward)
            del npc_data["reward"]  # 報酬獲得フラグの代わり

        # シナリオ遷移の確認
        novel_trigger = npc_data.get("novel_trigger")
        if novel_trigger:
            self.app.scene_state = 2  # SCENE_VN
            self.app.vn.start(novel_trigger)

        # マップ遷移の確認
        map_trigger = npc_data.get("map_trigger")
        if map_trigger:
            dest_x = npc_data.get("map_dest_x")
            dest_y = npc_data.get("map_dest_y")
            self.app.field._start_transition(map_trigger, dest_x, dest_y)

        self._close_dialog()

    # --- クイズ処理 ---

    def _handle_quiz(self, keys):
        """クイズ中の選択肢移動と決定処理"""
        if not self.current_quiz:
            return

        choices = self.current_quiz.get("choices", [])

        # 選択肢の移動
        if keys.get("up"):
            self.quiz_choice = (self.quiz_choice - 1) % len(choices)
        elif keys.get("down"):
            self.quiz_choice = (self.quiz_choice + 1) % len(choices)

        # 決定
        elif keys.get("z"):
            self._evaluate_quiz_answer()

    def _evaluate_quiz_answer(self):
        """クイズの正誤判定"""
        q = self.current_quiz
        npc_data = self.dialogues.get(self.active, {})

        if self.quiz_choice == q.get("answer", 0):
            # 正解時：報酬を付与し、クイズ完了フラグを立てる
            reward = q.get("reward")
            if reward:
                self.app.items.extend(reward)
            npc_data["quiz_done"] = True

        self._close_dialog()

    # --- インターフェース ---

    def try_talk(self):
        """プレイヤーの周囲にNPCがいるか確認し、会話を開始する"""
        if self.is_active() or self.wait_frames > 0:
            return

        px, py = self.app.x, self.app.y

        for key, data in self.dialogues.items():
            pos = data.get("position")
            if not pos:
                continue

            # マンハッタン距離が1（隣接）しているか判定
            if abs(pos[0] - px) + abs(pos[1] - py) == 1:
                self.active = key
                self._open_dialog(data)
                return

    def _open_dialog(self, data):
        """会話ウィンドウを開く"""
        self.window_lines = data.get("lines", [])
        self.line_index = 0
        self.quiz_mode = False
        self.current_quiz = None
        self.wait_frames = 15

    def _close_dialog(self):
        """会話ウィンドウを閉じる"""
        self.active = None
        self.window_lines = []
        self.line_index = 0
        self.quiz_mode = False
        self.current_quiz = None
        self.wait_frames = 20  # 閉じた直後の誤動作防止

    def is_active(self):
        """現在会話中かどうかを返す"""
        return self.active is not None

    # --- 描画処理 ---

    def draw(self, screen, font):
        """会話またはクイズウィンドウの描画"""
        if not self.is_active():
            return

        # ウィンドウサイズと位置の計算
        sw, sh = screen.get_size()
        ww, wh = sw * 0.8, sh * 0.3
        wx, wy = (sw - ww) // 2, sh - wh - 20
        rect = (wx, wy, ww, wh)

        if self.quiz_mode and self.current_quiz:
            # クイズ表示
            q = self.current_quiz
            display_lines = [q.get("question", "")]

            # 選択肢の構築
            for i, choice in enumerate(q.get("choices", [])):
                cursor = ">" if i == self.quiz_choice else " "
                display_lines.append(f"{cursor} {i + 1}. {choice}")

            draw_window(screen, font, display_lines, rect)

        elif self.window_lines:
            # 通常会話表示
            idx = min(self.line_index, len(self.window_lines) - 1)
            draw_window(screen, font, [self.window_lines[idx]], rect)
