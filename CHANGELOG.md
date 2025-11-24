# CHANGELOG of PBL-Game

## v0.17.1 (2025-11-24)
- バージョン表記方法の変更
- `src/` 下のファイルにおいて、相対 import を絶対 import に変更
- `src/__init__.py` を追加
  - **空ファイルだが、実行時に必要なので削除しないこと**

## v0.17.0 (2025-11-22)
- マップごとの BGM 管理機能の追加
- `assets/data/maps.json` の各ワールドのキーに `bgm` を追加し、BGM ファイルを指定する。
  - BGM ファイルは `assets/sounds/` にあるという前提

## v0.16.1 (2025-11-22)
- NPC に話しかけられないバグの修正
  - NPC の四近傍にいて、かつ、`Z` キーを押したときにのみ会話を開始するようにした

## v0.16.0 (2025-11-22-issa)
- `assets/data` のフォルダ作成
- 画面左上に現在の座標を表示
- `field.py` を大幅に書き換え、json をもとに map 遷移するアルゴリズムへ

## v0.15.0 (2025-11-22)
- BGM 追加
- BGM ファイルは `assets/sounds/` に入れる

## v0.14.0 (2025-11-21)
- **フォルダ構造の変更**
  <details>
  <summary>フォルダ構造を表示する</summary>

  ```
  PBL-Game
  ├── assets
  │   ├── dialogues
  │   │   └── dialogues.json
  │   ├── img
  │   │   ├── player_back.png
  │   │   ├── player_front.png
  │   │   ├── player_right.png
  │   │   ├── title.jpg
  │   │   ├── transition.jpg
  │   │   └── world_map.png
  │   └── sounds
  │       ├── chestclose.mp3
  │       └── chestopen.mp3
  ├── src
  │   ├── core
  │   │   ├── field.py
  │   │   ├── system.py
  │   │   └── talk.py
  │   ├── app.py
  │   ├── main.py
  │   ├── ui.py
  │   └── utils.py
  ├── .gitignore
  ├── CHANGELOG.md
  ├── LICENSE
  └── README.md
  ```

  </details>

- タイトル画像のファイル名を変更 ; `960.jpg` -> `title.jpg`
- `assets/` フォルダを追加し、ここに `img/`, `sounds/`, `dialogues/dialogues.json`を移動
- `src/` にソースコードを移動
- NPC 描画サイズを調整できるように修正
- `dialogues/dialogues.json` の NPC 座標を 2 要素形式に変更
- `field.py`, `talk.py` 内の NPC 表示・会話処理の修正
- 実行方法変更 ; `python -m src.main` で実行

## v0.13.0 (2025-11-18)
- プレイキャラクターの画像を移動方向に合わせて表示
- `player_front.png`, `player_back.png`, `player_right.png`のプレイキャラクターの前後左右画像を追加
- `player1.png` キャラクター仮画像の削除

## v0.12.0 (2025-11-18)
- プレイキャラクターの画像表示
- `player1.png` プレイヤー画像(仮)の追加(移動時の方向に合わせて、前後左右のキャラ画像に変更予定)
- キャラの解像度に合わせてタイルサイズを16に一旦変更

## v0.11.0 (2025-11-18)
- 効果音追加
- 音源は `sounds/` で管理

## v0.10.0 (2025-11-18)
- ワールド遷移時のアイリスアウト、アイリスインのアニメーション追加

## v0.9.1 (2025-11-18-issa)
- field.pyの変更
  - 画面のサイズをでかく(キャラクターの解像度が決まり次第タイルサイズを変更予定)
  - キー押下で連続移動できるように変更
  - `self.speed` は移動速度を変更できる  
    `offset` は1タイル分のピクセル数、`TILE=60` と定義されているなら1マス60px、`offset+=self.speed` としているのでspeedを変化させると移動速度が上がる

## v0.9.0 (2025-11-18)
- ワールド遷移の実装

## v0.8.2 (2025-11-18)
- 画面外に出られないように

## v0.8.1 (2025-11-18)
- 移動時のカクツキを解消

## v0.8.0 (2025-11-11)
- 全体マップ（世界地図）アセットの追加
- `img/` フォルダに `world_map.png` を追加
- プレイヤーを中心に世界地図がスクロールするように

## v0.7.0 (2025-11-04)
- 起動画面の追加
- `img/` フォルダの追加(画像ファイルはここに追加し、参照するように)

## v0.6.0 (2025-11-04)
- **ゲームエンジンを `Pygame` に変更**

## v0.5.2 (2025-11-04)
- 起動不能バグの修正
- `README.md` の加筆修正、日本語化

## v0.5.1 (2025-11-04)
- `assets.pyxres` の追加
- `k8x12S.bdf` の追加

## v0.5.0 (2025-11-03)
- `CHANGELOG.md` の日本語化
- コードの説明を追加
- 将来的なテクスチャ、BGM 追加に対応

### 対応予定
| 種類 | 対応箇所 | 備考 |
| :---: | :---: | :---: |
| プレイヤー表示 | `core/field.py` 内 `# プレイヤー描画` | `px.blt(56, 56, 0, 0, 0, 16, 16, 0)` |
| NPC 表示 | `core/field.py` 内 `# NPC描画` | `px.blt(screen_x, screen_y, 0, 16, 0, 16, 16, 0)` |
| タイルマップ | `core/field.py` 内 `# 将来的なアセット対応` | `px.bltm()` 利用 |
| BGM | `core/system.py` | `px.playm(track_id, loop=True)` |
| SE | `core/field.py`，`core/talk.py` | `px.play()` を適宜挿入 |

**BGM**
| 機能 | 実装箇所 | 備考 |
| :---: | :---: | :---: |
| BGM再生 | `System.play_bgm()` | `px.playm(track_id, loop=True)` を有効化 |
| BGM停止 | `System.stop_bgm()` | `px.stop()` を有効化 |
| 歩行音 | `Field.start_move()` | `px.play()` を追加 |
| 会話開始BGM切替 | `Talk.open_dialog()` | `self.app.system.play_bgm(track_id)` |
| クイズ正解／不正解SE | `Talk.update()` | `px.play(3, 2)` / `px.play(3, 3)` |

## v0.4.0 (2025-11-02)
- `/src` 以下を大幅に変更し、新たなテンプレートに置き換え

## v0.3.0 (2025-10-28)
- `src/main.py` に <https://github.com/shiromofufactory/pyxel-tiny-drpg> から引用
- `src/sample.py` を削除

## v0.2.1 (2025-10-28)
- リファクタリング

## v0.2.0 (2025-10-28)
- `pyxel` のサンプルを追加

## v0.1.0 (2025-10-28)
- リポジトリ作成
- プロジェクト開始