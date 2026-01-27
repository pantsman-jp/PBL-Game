# The Journey to Rocket Launch _- YOU CAN (NOT) TRY AGAIN -_

## 概要
このゲームは、**宇宙工学・宇宙理学の面白さを高校生に紹介する** というコンセプトで開発されています。

## 遊び方
開発環境を用意せずに遊びたい場合は、[こちら](https://github.com/pantsman-jp/PBL-Game/releases/tag/demo)
からデモ版をダウンロードしてください。

## 開発者向け

### インストール方法
```
git clone https://github.com/pantsman-jp/PBL-Game
```

### 使い方
以下の環境で動作確認済みです。

- `Python 3.13.9 ~ 3.13.11`
- `numpy 2.4.0 ~ 2.4.1`
- `pygame 2.6.1`
- `pyinstaller 6.17.0 ~ 6.18.0`

後述する `Makefile` および `tools.ps1` を用いた実行ファイルの作成方法は、
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

ただし、ゲーム内で使用している画像、音声等のアセットについては、
各素材提供元のライセンス条件が優先して適用されます。
これらは [MIT License](LICENSE) の適用範囲には含まれません。
アセットの再配布・改変・商用利用にあたっては、下記の素材出典を参考に必ず各提供元の規約をご確認ください。

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
