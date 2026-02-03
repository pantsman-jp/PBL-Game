<h1 align="center">
  The Journey to Rocket Launch<br>- YOU CAN (NOT) TRY AGAIN -
</h1>

## 概要
このゲームは、ロケット開発を題材にした探索・ノベル要素を含む 2D ゲームです。
**宇宙工学・宇宙理学の面白さを高校生に紹介する** ことを目的として開発されました。

プレイヤーは物語を通して、宇宙開発に関わる概念や考え方に触れていきます。

## 遊び方
開発環境を用意せずに遊びたい場合は、[こちら](https://github.com/pantsman-jp/PBL-Game/releases)
から最新リリースをダウンロードしてください。

ゲーム開始後、プレイヤーはマップ上を移動し、NPC との会話やイベントを通じて物語を進行させます。
物語の進行に伴い、ロケット開発に関する要素が段階的に提示されます。

## 開発者向け

### インストール方法
```
git clone git@github.com:pantsman-jp/PBL-Game.git
```

### 使い方
以下の環境で動作確認済みです。

- `Python 3.13.9 ~ 3.13.11`
- `numpy 2.4.0 ~ 2.4.1`
- `pygame 2.6.1`
- `pyinstaller 6.17.0 ~ 6.18.0`

後述する `makefile` および `tools.ps1` を用いた実行ファイルの作成方法は、
仮想環境（`venv`）の使用を前提としています。事前に仮想環境を構築してください。

パッケージは次のコマンドでインストールします。

```
pip install -r requirements.txt
```

ゲームを起動するには、ルート直下で以下のコマンドを実行します。

```
python -m src.main
```

### 実行ファイル作成
以下のコマンドはルート直下で実行します。

#### Windows
> [!WARNING]
> 下記コマンドは PowerShell の実行ポリシーを **プロセス単位で一時的に変更** します。
> 内容を理解した上で実行してください。

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
. .\tools.ps1
build
```

#### macOS
```
make build
```

## 免責事項
本ゲームの利用に際しては [免責事項](docs/disclaimer.ja.md) をご確認ください。

## ライセンス
本プロジェクトのソースコードは [MIT License](LICENSE) の下で公開されています。

なお、ゲーム内で使用している画像、音声等のアセットについては、
各素材提供元のライセンス条件が適用されます。
これらは [MIT License](LICENSE) の適用範囲には含まれません。

アセットの再配布・改変・商用利用にあたっては、**必ず**下記の素材出典から各提供元の規約をご確認ください。

### 素材出典
| 使用箇所 | 素材元・作者名 | URL |
| :---: | :---: | :---: |
| プレイヤー、NPC | ぴぽや倉庫 | <https://pipoya.net/sozai/> |
| タイトル・エンディング画面 <br> ノベルパート| AIPICT | <https://aipict.com/> |
| エンディング画面 <br> ノベルパート| photoAC | <https://www.photo-ac.com> |
| エンディング画面 | Image Credit: NASA | <https://www.nasa.gov/nasa-brand-center/images-and-media/> |
| 都道府県マップ | RPG風イラストマップ | <https://rpgmap.hatenablog.com/> |
| マップ BGM | DOVA-SYNDROME | <https://dova-s.jp/> |
| 効果音 | 効果音ラボ | <https://soundeffect-lab.info/> |
| 音楽 | Kevin MacLeod | "Blue Danube (by Strauss)" (CC By 4.0) |

---
Copyright © 2025-2026 [@pantsman](https://github.com/pantsman-jp), [@ISSA-Motomu](https://github.com/ISSA-Motomu), [@tanosou](https://github.com/tanosou), [@osato03](https://github.com/osato03), [@nagata](https://github.com/Yusuke-NAGATA), [@Shiba600](https://github.com/Shiba600)
