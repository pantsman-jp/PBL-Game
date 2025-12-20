"""
ビジュアルノベル管理 | src/core/visual_novel.py
立ち絵、背景、テキストウィンドウによる会話イベントを制御
"""

import pygame
import os
from src.utils import resource_path, load_json
from src.ui import draw_window

class VisualNovel:
    """
    ノベルパート（Visual Novel Part）を管理するクラス
    
    VN(Visual Novel):
      会話イベントの処理を行う
      > 背景、立ち絵、テキストボックスを用いて物語を進行させる形式のゲームジャンル
    
    機能:
        - JSONスクリプトの読み込みと再生
        - 背景画像と立ち絵の表示切り替え
        - テキストウィンドウの描画とページ送り
    """
    def __init__(self, app):
        self.app = app
        self.script = []
        self.index = 0
        self.active = False
        self.bg_image = None
        self.char_image = None
        self.base_dir = resource_path("assets")
        
        # スクリプトデータの読み込み
        # assets/data/novel_scripts.jsonからシナリオロード
        scripts_path = os.path.join(self.base_dir, "data", "novel_scripts.json")
        self.scripts_data = load_json(scripts_path) or {}

        # デフォルトのフォントを使用
        self.font = app.font

    def start(self, script_id):
        """
        指定されたIDのスクリプトを開始
        
        Args:
            script_id (str): novel_scripts.json 内のキー（例: "opening"）
        """
        if script_id not in self.scripts_data:
            print(f"Script ID not found: {script_id}")
            self.end_scene()
            return

        self.script = self.scripts_data[script_id]
        self.index = 0
        self.active = True
        self._load_current_scene()

    def _load_current_scene(self):
        """
        - 現在の進行度(self.index)に基づいて、画面を更新
        - スクリプト末尾なら終了処理
        """
        if self.index >= len(self.script):
            self.end_scene()
            return

        data = self.script[self.index]
        
        # 背景画像のロード (指定がある場合のみ更新)
        bg_name = data.get("bg")
        if bg_name:
            path = os.path.join(self.base_dir, "img", bg_name)
            if os.path.isfile(path):
                self.bg_image = pygame.image.load(path).convert()
                # 画面サイズに合わせてスケール（必要に応じて）
                self.bg_image = pygame.transform.scale(self.bg_image, (900, 700))

        # 立ち絵のロード (指定がある場合のみ更新、"none"で消去)
        char_name = data.get("char")
        if char_name:
            if char_name.lower() == "none":
                self.char_image = None
            else:
                path = os.path.join(self.base_dir, "img", char_name)
                if os.path.isfile(path):
                    img = pygame.image.load(path).convert_alpha()
                    # 立ち絵のサイズ調整（例: 高さ400pxに合わせるなど）
                    # ここではそのまま表示
                    self.char_image = img

    def update(self, events):
        """
        - 入力処理
          - Click or Spaceキーで次のメッセージへ
        """
        if not self.active:
            return

        for ev in events:
            # クリックまたはスペースキーで次のメッセージへ
            if ev.type == pygame.MOUSEBUTTONDOWN or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE):
                self.index += 1
                self._load_current_scene()

    def draw(self, screen):
        """
        - ノベルパートの描画
          - 背景->立ち絵->テキストウィンドウの順に重ねて描画
        """
        if not self.active:
            return

        # 背景描画
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # 立ち絵描画 (画面中央下部に配置する例)
        if self.char_image:
            rect = self.char_image.get_rect(midbottom=(450, 600))
            screen.blit(self.char_image, rect)

        # テキストウィンドウ描画
        if self.index < len(self.script):
            data = self.script[self.index]
            text = data.get("text", "")
            speaker = data.get("speaker", "")
            
            # 話者がいる場合は名前を表示
            lines = []
            if speaker:
                lines.append(f"【{speaker}】")
            lines.append(text)
            
            # 画面下部にウィンドウを表示
            draw_window(screen, self.font, lines, rect=(50, 500, 800, 150))

    def end_scene(self):
        """
        - ノベルパート終了処理
          - フラグを下ろし、RPGパート開始
        """
        self.active = False
        # ゲーム本編を開始するメソッドを呼び出す
        self.app.start_rpg_game()
