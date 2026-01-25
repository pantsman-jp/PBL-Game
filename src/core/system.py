"""
システム管理 | src/core/system.py
セーブ/ロードおよびBGM制御を提供
"""

import os
import pygame
from src.utils import save_json, load_json, SAVEFILE, resource_path


class System:
    """
    ゲームの進行フラグ、セーブデータ、音響再生を統括するクラス
    """

    def __init__(self, app):
        self.app = app
        self.savefile = SAVEFILE

        # ゲーム進行フラグの初期化
        self.flags = {
            "intro_done": False,
            "item_cfrp": False,
            "item_engine": False,
            "item_cpu": False,
            "rocket_assembled": False,
        }

    # --- フラグ操作 ---

    def set_flag(self, key, value=True):
        """フラグの状態を設定"""
        self.flags[key] = value

    def get_flag(self, key):
        """フラグの状態を取得（存在しない場合はFalse）"""
        return self.flags.get(key, False)

    # --- 目的（Objective）管理 ---

    def get_current_objective(self):
        """
        現在のフラグ状態に基づいて、画面上部に表示する目標テキストを生成する
        """
        current_map = self.app.field.current_map_id

        # 1. エンジン (C6-0) チェック
        if "model_rocket_engine_c6_0" not in self.app.items:
            return "目標：九州工業大学(座標(214,104))に向かい、モデルロケットエンジンを入手せよ"

        # 九工大マップから出れない人用
        if current_map == "kyutech_campus":
            return "目標：出口は(15,16)付近にある。外へ出よう！"

        # 2. 部品収集フェーズ
        # CFRP
        if "aichi_cfrp_sheet" not in self.app.items:
            if current_map == "world":
                return "目標：愛知県へ向かい、構造用CFRPシートを入手せよ"
            else:
                return "目標：名古屋城（座標（/,/））付近にいるNPCに話しかけてCFRPを入手せよ"

        # 制御基板
        if "kanagawa_control_unit" not in self.app.items:
            if current_map == "world" or current_map == "aichi":
                return "目標：神奈川県へ向かい、制御基板を入手せよ"
            else:
                return "目標：JAXA相模原キャンパス（座標（/./））付近にいるNPCに話しかけて制御基板を入手せよ"

        # アンテナ
        if "ibaraki_antenna_module" not in self.app.items:
            if current_map in ["world", "aichi", "kanagawa"]:
                return "目標：茨城県へ向かい、アンテナを入手せよ"
            else:
                return "目標：筑波宇宙センター（座標（/./））付近にいるNPCに話しかけてアンテナを入手せよ"

        # エンジンユニット
        if "kagoshima_engine_unit" not in self.app.items:
            if current_map in ["world", "aichi", "kanagawa", "ibaraki"]:
                return "目標：鹿児島県へ向かい、エンジンユニットを入手せよ"
            else:
                return "目標：鹿児島県種子島の座標(/,/)のNPCに話しかけてエンジンユニットを入手せよ"

        # 3. 最終フェーズ デモ版では、組み立てる段階を作れなさそうので直接打ち上げへ
        # if not self.flags["rocket_assembled"]:
        #    return "目標：部品は揃った。ロケットを組み立てろ！"

        return "目標：種子島のどこかにいるNPCを探し、ロケットを打ち上げろ！"

    # --- データ永続化（セーブ・ロード） ---

    def save(self):
        """現在のプレイヤー座標、所持アイテム、フラグを保存"""
        data = {
            "x": self.app.x,
            "y": self.app.y,
            "items": self.app.items,
            "flags": self.flags,
        }

        try:
            save_json(self.savefile, data)
            print(f"System: Successfully saved to {self.savefile}")
        except Exception as e:
            print(f"System: Save Error! - {e}")

    def load(self):
        """保存されたデータを読み込み、アプリの状態を復元"""
        data = load_json(self.savefile)
        if not data:
            return False

        try:
            self.app.x = data.get("x", self.app.x)
            self.app.y = data.get("y", self.app.y)
            self.app.items = data.get("items", [])
            self.flags = data.get("flags", self.flags)

            print(f"System: Successfully loaded from {self.savefile}")
            return True
        except Exception as e:
            print(f"System: Load Error! - {e}")
            return False

    # --- BGM制御 ---
    def play_bgm(self, path):
        if not pygame.mixer.get_init() or not path:
            return

        full_path = resource_path(path)
        print("DEBUG: play_bgm full_path =", full_path)
        print("DEBUG: play_bgm called for", full_path)
        if not os.path.isfile(full_path):
            print("BGM not found:", full_path)
            return

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"System: BGM Playback Error - {e}")

    def stop_bgm(self):
        # ミキサーが使用可能かチェック
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
