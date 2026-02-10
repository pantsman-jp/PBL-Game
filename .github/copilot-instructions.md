# Copilot / AI エージェント向けガイド — PBL-Game

目的：このファイルは、AI コード補助エージェントがこのリポジトリで素早く安全に作業できるための「実務上の知識」をまとめます。

- 簡単な概要
  - プロジェクトはタイルベースの 2D フィールドと会話（VN/クイズ）を持つ教育ゲームです。
  - データ駆動設計：NPC・マップ・会話は JSON（主に `assets/dialogues/dialogues.json` と `assets/data/maps.json`）で管理されます。

- 重要なファイル（まず参照する）
  - `src/core/field.py`：マップ読み込み、描画、プレイヤー移動、NPC 描画（`_draw_npcs`）や移動ブロック判定（`start_move`）を含む。
  - `src/core/talk.py`：`dialogues.json` をロードして会話・クイズ・報酬・マップ遷移トリガーを扱う（`try_talk`, `_finalize_conversation` を確認）。
  - `assets/dialogues/dialogues.json`：各 NPC の定義（`position`, `map_id`, `image`, `movement_x`, `quiz`, `map_trigger`, `novel_trigger`, `reward` 等）。
  - `assets/data/maps.json`：マップ定義、`exits`（x,y と target_map, dest_x/dest_y）を持つ。`Field.load_map` が参照する。
  - `src/main.py`：起動エントリ。実行コマンドはルートから `python -m src.main` か `python src/main.py`。

- NPC 配置に関する「事実」/コーディングの重要点（必ず守る）
  - 座標単位はタイル（整数）です。`position` は `[x, y]`（タイル座標）。
  - NPC は `assets/dialogues/dialogues.json` の各エントリで定義され、ランタイムで `Talk.dialogues` に読み込まれます。
  - `Field.start_move` はプレイヤーが移動しようとする先に NPC がいると移動をキャンセルします（NPC は移動をブロックする実装）。
  - 会話開始は `Talk.try_talk()` がプレイヤーの四近傍（マンハッタン距離 1）に NPC がいるかを調べて行います。
  - NPC の揺らぎ（左右移動）は `movement_x` フィールドで制御（`enabled`, `speed`, `max_offset`）。描画時に `image` を `assets/img/<image>` から読み込み、拡大してキャッシュします（`image_surface_zoom`）。
  - 会話処理で JSON オブジェクトはランタイムに変更されます（例：`reward` を `del` で消す、`quiz_done` をセット）。永続的に変更したい場合は JSON を編集してコミットする必要あり。

- 具体的な編集手順（NPC を追加/移動する場合）
  1. `assets/dialogues/dialogues.json` に新しいキーを追加し、`position`, `map_id` を設定する。
  2. 必要なら `image` に `character/<file>.png` を指定し、`assets/img/character/` に画像を置く。
  3. 動く NPC にするなら `movement_x` を設定する（例：`{"enabled": true, "speed": 0.5, "max_offset": 8}`）。
  4. マップ遷移トリガーを持たせるには `map_trigger`, `map_dest_x`, `map_dest_y` を追加する。
  5. 変更をローカルで動作確認するにはルートからアプリを起動して、該当マップで NPC の位置と会話が期待通りか確認する。

- 実装パターン・注意点（AI が自動変更するときのチェックリスト）
  - 座標はタイル単位：間違えてピクセル値を入れない（`TILE = 10`、`ZOOM = 2` は `src/core/field.py` を参照）。
  - NPC がプレイヤー移動をブロックする点を意図的に変えるなら、`Field.start_move` の NPC チェックを編集する必要がある（副作用を考慮する）。
  - 会話やクイズのロジックは `Talk._finalize_conversation` に複雑な分岐がある（報酬付与、map_trigger と novel_trigger の扱い、アイテム要件チェック）。ここを変更する場合は既存のフローを壊さないようユニットチェックを行う。
  - `dialogues.json` の構造を変える変更は、`Talk` のロード・参照箇所をすべて更新する必要がある（`try_talk`, `_open_dialog`, `_advance_to_next_state` 等）。

- 実行・デバッグのコマンド例
```bash
# ルートから
python -m src.main
# または
python src/main.py
```

- テスト方針（手動チェックの最短手順）
  - 変更後、ゲームを起動 → 該当マップへ移動 → NPC の表示位置・画像・動作を確認 → `Z` で会話する。会話で報酬を与える場合、`app.items` の内容を確認。

- 追加情報や変更を求めるときに AI に伝えるべき具体事項
  - どの NPC（キー名）を追加/移動するのか（例：`npc_7`）、目的の `map_id` と `position`（タイル座標）
  - 画像ファイル名（既存か新規か）、移動パターン（`movement_x` の具体値）
  - 会話の変化（`lines` や `quiz` の追加）によっては `Talk` 側のロジック調整が必要かどうか

---
このファイルを元に修正提案や自動パッチを作成できます。補足してほしい箇所（例：`Talk._finalize_conversation` の分岐説明やマップ `exits` の詳細）を教えてください。
# PBL-Game Copilot Instructions

## Project Overview
This is a Pygame-based educational game combining RPG field exploration with visual novel storytelling to teach high school students about space engineering and astrophysics. The game features scene-based architecture with three main states: title screen, RPG gameplay, and visual novel sequences.

## Architecture
- **Scene Management**: `App` class manages three scenes (SCENE_TITLE=0, SCENE_GAME=1, SCENE_VN=2) via `scene_state`. Each scene has dedicated update/draw logic.
- **Core Components**:
  - `Field`: Handles RPG map rendering, player movement, NPC interactions, and map transitions
  - `Talk`: Manages NPC dialogues and quiz systems with reward mechanics
  - `VisualNovel`: Controls VN sequences with background/character images and text windows
  - `System`: Provides save/load functionality and BGM control
- **Data Flow**: Pygame event loop → `_handle_events()` → `_update()` → `_draw()` per frame

## Key Workflows
- **Run Game**: `python -m src.main` (requires Python 3.13.9 + Pygame 2.6.1)
- **Save/Load**: Press 'S' in game to save to `save.json`; auto-loads on startup
- **Debug**: Check console for JSON load errors; use `traceback` in `main.py` for exceptions

## Coding Patterns
- **Resource Loading**: Use `resource_path()` from `utils.py` for cross-platform asset paths (e.g., `resource_path("assets/img/title.jpg")`)
- **Input Handling**: Use `KeyTracker` for press-once detection; keys mapped as `{"z": advance, "q": quit, "up/down": navigate}`
- **Data Management**: Store game data in JSON files under `assets/data/`; use `load_json()`/`save_json()` for persistence
- **UI Rendering**: Draw text windows with `draw_window()` from `ui.py`; position at bottom (320-448 y-coords)
- **Quiz System**: In `Talk`, handle multiple choice with arrow keys; correct answers add items to `app.items` list

## Integration Points
- **Asset Dependencies**: Images in `assets/img/`, sounds in `assets/sounds/`, data in `assets/data/`
- **External Libraries**: Pygame for graphics/audio; no web APIs or databases
- **Cross-Component Communication**: Components access shared `app` instance for state (e.g., `self.app.items`, `self.app.scene_state`)

## Examples
- Add new dialogue: Edit `assets/dialogues/dialogues.json` with quiz options and rewards
- Modify VN script: Update `assets/data/novel_scripts.json` with background/char image paths
- Extend inventory: Items stored as strings in `app.items`; display in game UI with comma separation