# CHANGELOG of PBL-Game

## v0.22.0 (2025-12-20)
- `maps.json` での衝突判定を廃止
  - これに伴い `make_collision.py` を削除
- 定数 `TILE` を 16 から 10 へ変更
- 表示倍率を制御する定数 `ZOOM` および `Z_TILE` を導入
- 描画中心座標 `SCREEN_CENTER_X` および `SCREEN_CENTER_Y` を App クラスの解像度（900x700）に合わせて更新
- 海判定（移動不可判定）ロジックを移動先タイルの中心1ピクセルのみを参照する方式へ簡略化
- `load_map` メソッドに、描画負荷軽減のための事前拡大イメージ `map_image_zoom` の生成処理を追加
- `load_player` メソッドに、プレイヤー画像の事前拡大処理を追加し、画像不在時の代替サーフェスサイズを `Z_TILE` に同期
- draw メソッド内の描画計算式を、タイル座標に `Z_TILE` を乗算し ZOOM 加味のオフセットを加算する形式へ刷新
- プレイヤーの描画位置を画面中央に固定し、マップ側がスクロールする描画仕様へ変更
- NPCの描画および移動オフセット、ラベル表示位置を拡大率に合わせて再計算するよう修正
- 画面遷移（トランジション）の円の描画位置と速度を拡大後の画面サイズに合わせて調整

## v0.21.2 (2025-12-20)
- 従来の「タイル中心ピクセル基準」を廃止
- プレイヤーの足元位置を基準点として海／陸判定を行う方式に変更
- 単純な 3×3（9点）の同一重み多数決を廃止
- 重み付き投票方式を導入
  - 足元直下を最優先
  - 左右および直上を中優先
  - 斜め方向を補助的扱い

## v0.21.1 (2025-12-20)
- 海判定ロジックを 単一ピクセル判定 から 多数決方式 に変更した。
  - 各タイルについて、**中央を含む 3×3 ピクセル（計 9 ピクセル）**を対象にする。
  - 9 ピクセルのうち 半数以上（5 以上）が海色の場合のみ、そのタイルを海と判定する。

## v0.21.0 (2025-12-20-issa)
- visual_novel.pyの新規作成
- app.pyの変更
- novel_script.jsonの新規作成
  > 会話の内容を書く

## v0.20.0 (2025-12-20)
- NPC ごとに表示画像を指定できる仕組みを追加
- `assets/dialogues/dialogues.json` に `image` フィールドを追加することで、NPC 画像ファイル名を指定可能
- NPC 画像を `assets/img/` から読み込み、描画する処理を追加しました
- NPC の描画方法を、矩形描画から画像描画に変更
- NPC を示すための固定色矩形描画処理を削除

## v0.19.1 (2025-12-16)
- `assets/` 内の素材の変更

| 使用箇所 | 出典 |
| :---: | :---: |
| プレイヤー | <https://pipoya.net/sozai/terms-of-use/> |
| タイトル | <https://aipict.com/terms-of-use/> |
| 福岡県マップ | <https://rpgmap.hatenablog.com/> |
| マップ BGM | <https://dova-s.jp/> |
| 効果音 | <https://soundeffect-lab.info/> |

## v0.19.0 (2025-12-09-issa)
- 所持アイテムの欄と、座標の表示を重ならないようにしました
- NPCと話しただけでitemがもらえる機能追加
  - npc2でpart1を入手
- rewardを`[item1],[item2]`のようにリスト形式に
- itemの重複取得禁止
  > NPCからitemを取得したら、json上のデータをdeleteすることで、二回以上話しかけてもアイテムの重複取得が行われないようにする

## v0.18.1 (2025-12-08)
- `src/utils.py` に `resource_path` 関数を追加し、PyInstaller 実行時にファイルが見つからない問題に対応
- `app.py` および `field.py` 内で `BASE_DIR` を `resource_path("assets")` を利用する形に変更
- BGM 再生処理を `resource_path` を経由してファイルパスを取得するよう修正
  - 画像や JSON など外部リソース読み込み箇所も同様
- `docs/` に免責事項を追加

## v0.18.0 (2025-11-25)
- NPC_1のみが左右に動くように
- 移動させるかどうか,速度(speed),距離(max_offset),はdialogues.jsonでNPCごとにパラメータ管理
- 移動方向はfield.pyのscreen_x,screen_yの部分で管理
- 現在は左右移動のみ、今後はNPCごとに異なる動きを実装予定

## v0.17.1 (2025-11-24)
- バージョン表記方法の変更
- `src/` 下のファイルにおいて、相対 import を絶対 import に変更
- `src/__init__.py` を追加
  - **空ファイルだが、実行時に必要なので削除しないこと**
  - 実行ファイル化のために必要です

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
