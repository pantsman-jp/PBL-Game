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

        # --- 状態管理変数の初期化（ここが漏れるとエラーになります） ---
        self.active = None  # 現在会話中のNPCキー
        self.window_lines = []  # 表示するテキストリスト
        self.line_index = 0  # 現在の行番号
        self.quiz_mode = False  # クイズ中か
        self.quiz_result_mode = False  # クイズ結果の表示中か
        self.current_quiz = None
        self.quiz_choice = 0
        self.quiz_index = 0  # 複数クイズのインデックス
        self.quiz_text_input = ""  # テキスト入力モード時の入力内容
        self.wait_frames = 0

    def is_active(self):
        """現在会話中（ウィンドウが表示されるべき状態）か判定"""
        return self.active is not None

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

        # クイズ選択中の操作
        if self.quiz_mode and not self.quiz_result_mode:
            self._handle_quiz(keys)
        else:
            # 通常会話、またはクイズ結果表示中の操作
            self._handle_dialog(keys)

    def _handle_dialog(self, keys):
        """通常のテキスト送りの処理"""
        if keys.get("z"):
            self.line_index += 1

            # 全ての行を読み終えた場合
            if self.line_index >= len(self.window_lines):
                if self.quiz_result_mode:
                    self._close_dialog()  # 結果を読み終えたら終了
                else:
                    self._advance_to_next_state()

    def _advance_to_next_state(self):
        """テキスト終了後の遷移判定（クイズへ行くか、終了するか）"""
        npc_data = self.dialogues.get(self.active, {})
        quiz = npc_data.get("quiz")

        # 未達成のクイズがある場合はクイズモードへ
        if quiz and not npc_data.get("quiz_done"):
            self.quiz_mode = True
            if isinstance(quiz, list):
                self.quiz_index = 0
                self.current_quiz = quiz[self.quiz_index]
            else:
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

        # マップ遷移の確認（ノベル前にセット）
        map_trigger = npc_data.get("map_trigger")
        if map_trigger:
            novel_trigger = npc_data.get("novel_trigger")
            if map_trigger == "ending":
                # エンディング遷移は特別処理
                self.app.scene_state = 2  # SCENE_VN
                self.app.vn.start(novel_trigger)
                self._close_dialog()
            dest_x = npc_data.get("map_dest_x", 10)
            dest_y = npc_data.get("map_dest_y", 10)
            if novel_trigger:
                # 次の都道府県へ飛ぶ場合、アイテムチェック
                required_items = {
                    "aichi": "model_rocket_engine_c6_0",
                    "kanagawa": "aichi_cfrp_sheet",
                    "ibaraki": "kanagawa_control_unit",
                    "kagoshima": "ibaraki_antenna_module",
                    "ending": "kagoshima_engine_unit",
                }
                required_item = required_items.get(map_trigger)
                if required_item:
                    if required_item not in self.app.items:
                        self.window_lines = [
                            f"【{required_item}】を持っていないと進めないぞ。"
                        ]
                        self.line_index = 0
                        self.wait_frames = 15
                        return
                    else:
                        self.line_index = 0
                        self.wait_frames = 15
                        # 遷移は続行
                # アイテムがある場合、遷移
                self.app.stop_map_transition = (map_trigger, dest_x, dest_y)
            else:
                # 戻る場合、即時遷移
                self.app.field._start_transition(map_trigger, dest_x, dest_y)

        # シナリオ遷移の確認
        novel_trigger = npc_data.get("novel_trigger")
        if novel_trigger:
            self.app.scene_state = 2  # SCENE_VN
            self.app.vn.start(novel_trigger)

        self._close_dialog()

    # --- クイズ処理 ---

    def _handle_quiz(self, keys):
        """クイズ中の選択肢移動と決定処理"""
        if not self.current_quiz:
            return

        quiz_type = self.current_quiz.get("type", "choice")

        if quiz_type == "text":
            self._handle_text_quiz(keys)
        else:  # デフォルトは choice
            self._handle_choice_quiz(keys)

    def _handle_choice_quiz(self, keys):
        """3択問題の処理"""
        choices = self.current_quiz.get("choices", [])

        # 選択肢の移動
        if keys.get("up"):
            self.quiz_choice = (self.quiz_choice - 1) % len(choices)
        elif keys.get("down"):
            self.quiz_choice = (self.quiz_choice + 1) % len(choices)

        # 決定
        elif keys.get("z"):
            self._evaluate_quiz_answer()

    def _handle_text_quiz(self, keys):
        """テキスト入力問題の処理"""
        # 半角数字およびピリオドの入力
        for ch in "0123456789.":
            if keys.get(ch):
                # ピリオドは1つまで
                if ch == "." and "." in self.quiz_text_input:
                    continue
                # 入力文字数は10文字までに制限
                if len(self.quiz_text_input) < 10:
                    self.quiz_text_input += ch

        # BackSpaceキーで入力削除
        if keys.get("backspace"):
            self.quiz_text_input = self.quiz_text_input[:-1]

        # 決定（Zキー）
        elif keys.get("z"):
            self._evaluate_text_quiz_answer()

    def _evaluate_quiz_answer(self):
        """クイズの正誤判定"""
        q = self.current_quiz
        npc_data = self.dialogues.get(self.active, {})
        quiz = npc_data.get("quiz")

        # 結果メッセージの構築
        result_lines = []
        if self.quiz_choice == q.get("answer", 1):  # jsonは1から始まるため
            if isinstance(quiz, list):
                self.quiz_index += 1
                if self.quiz_index >= len(quiz):
                    # すべて正解
                    result_lines.append("全問正解だ！素晴らしい。")
                    reward = npc_data.get("reward")
                    if reward:
                        for item_id in reward:
                            result_lines.append(f"【{item_id}】を手に入れた。")
                        self.app.items.extend(reward)
                    npc_data["quiz_done"] = True
                else:
                    # 次のクイズへ
                    result_lines.append("正解！次の問題だ。")
                    self.current_quiz = quiz[self.quiz_index]
                    self.quiz_choice = 0
                    self.window_lines = []
                    self.wait_frames = 15
                    return  # 結果表示せずに次のクイズへ
            else:
                result_lines.append("正解だ！素晴らしい。")
                reward = q.get("reward")
                if reward:
                    for item_id in reward:
                        result_lines.append(f"【{item_id}】を手に入れた。")
                    self.app.items.extend(reward)
                npc_data["quiz_done"] = True
        else:
            result_lines.append("残念、不正解だ。")
            if isinstance(quiz, list):
                result_lines.append("最初の問題からやり直しだ。")
                self.quiz_index = 0
                self.current_quiz = quiz[self.quiz_index]
            else:
                result_lines.append("もう一度挑戦してくれたまえ。")

        self.window_lines = result_lines
        self.line_index = 0
        self.quiz_result_mode = True
        self.wait_frames = 15

    def _evaluate_text_quiz_answer(self):
        """テキスト入力クイズの正誤判定"""
        q = self.current_quiz
        npc_data = self.dialogues.get(self.active, {})
        quiz = npc_data.get("quiz")

        # ユーザーの入力値と正解を比較
        user_answer = self.quiz_text_input.strip()
        correct_answer = str(q.get("answer", ""))

        result_lines = []
        if user_answer == correct_answer:
            if isinstance(quiz, list):
                self.quiz_index += 1
                if self.quiz_index >= len(quiz):
                    # すべて正解
                    result_lines.append("全問正解だ！素晴らしい。")
                    reward = npc_data.get("reward")
                    if reward:
                        for item_id in reward:
                            result_lines.append(f"【{item_id}】を手に入れた。")
                        self.app.items.extend(reward)
                    npc_data["quiz_done"] = True
                else:
                    # 次のクイズへ
                    result_lines.append("正解！次の問題だ。")
                    self.current_quiz = quiz[self.quiz_index]
                    self.quiz_text_input = ""
                    self.window_lines = []
                    self.wait_frames = 15
                    return  # 結果表示せずに次のクイズへ
            else:
                result_lines.append("正解だ！素晴らしい。")
                reward = q.get("reward")
                if reward:
                    for item_id in reward:
                        result_lines.append(f"【{item_id}】を手に入れた。")
                    self.app.items.extend(reward)
                npc_data["quiz_done"] = True
        else:
            result_lines.append("残念、不正解だ。")
            if isinstance(quiz, list):
                result_lines.append("最初の問題からやり直しだ。")
                self.quiz_index = 0
                self.current_quiz = quiz[self.quiz_index]
                self.quiz_text_input = ""
            else:
                result_lines.append("もう一度挑戦してくれたまえ。")

        self.window_lines = result_lines
        self.line_index = 0
        self.quiz_result_mode = True
        self.wait_frames = 15

    def try_talk(self):
        """プレイヤーの周囲にNPCがいるか確認し、会話を開始する"""
        if self.is_active() or self.wait_frames > 0:
            return

        px, py = self.app.x, self.app.y

        for key, data in self.dialogues.items():
            pos = data.get("position")
            if pos and abs(pos[0] - px) + abs(pos[1] - py) == 1:
                self.active = key
                self._open_dialog(data)
                break

    def _open_dialog(self, data):
        """会話ウィンドウを開く"""
        self.window_lines = data.get("lines", [])
        self.line_index = 0
        self.quiz_mode = False
        self.quiz_result_mode = False
        self.current_quiz = None
        self.quiz_index = 0
        self.quiz_text_input = ""
        self.wait_frames = 15

    def _close_dialog(self):
        """会話ウィンドウを閉じる"""
        self.active = None
        self.window_lines = []
        self.line_index = 0
        self.quiz_mode = False
        self.quiz_result_mode = False
        self.quiz_index = 0
        self.quiz_text_input = ""
        self.wait_frames = 20

    def draw(self, screen, font):
        """会話またはクイズウィンドウの描画"""
        if not self.is_active():
            return

        # ウィンドウサイズと位置の計算
        sw, sh = screen.get_size()
        rect = (sw * 0.1, sh - sh * 0.3 - 20, sw * 0.8, sh * 0.3)

        if self.quiz_mode and not self.quiz_result_mode:
            q = self.current_quiz
            quiz_type = q.get("type", "choice")

            if quiz_type == "text":
                # テキスト入力クイズの描画
                display_lines = [
                    q.get("question", ""),
                    f"入力: {self.quiz_text_input}_",
                ]
                draw_window(screen, font, display_lines, rect)
            else:
                # 3択クイズの描画
                display_lines = [q.get("question", "")]

                # 選択肢の構築
                for i, choice in enumerate(q.get("choices", [])):
                    cursor = ">" if i == self.quiz_choice else " "
                    display_lines.append(f"{cursor} {i + 1}. {choice}")

                draw_window(screen, font, display_lines, rect)

        elif self.window_lines:
            # 1行ずつ表示するための修正
            idx = min(self.line_index, len(self.window_lines) - 1)
            draw_window(screen, font, [self.window_lines[idx]], rect)
