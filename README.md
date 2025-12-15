# PBL-Game

## 概要
このゲームは、**宇宙工学・宇宙理学の面白さを高校生に紹介する** というコンセプトで開発されています。

## 免責事項
本プロジェクトの利用に際しては [免責事項](https://github.com/pantsman-jp/PBL-Game/blob/main/docs/disclaimer.ja.md) をご確認ください。 

## インストール方法
```
git clone https://github.com/pantsman-jp/PBL-Game
```

## 使い方
`Python3.13.9`, `Pygame2.6.1` が必要。

`Pygame` は以下でインストール。

```
pip install pygame
```

実行方法は以下。
```
python -m src.main
```

## 実行ファイル化の方法
### Windows
`Pyinstaller` が必要。以下のコマンドを実行してインストールする。

```
pip install pyinstaller
```

`PBL-Game/` 直下にて以下を実行し、実行ファイルを作成する。

```
pyinstaller --onefile --windowed --add-data "assets;assets" src\main.py
```

実行ファイルは `dist/` 直下に作成される。

### macOS
`Pyinstaller` インストールまでは同じ。コマンドは以下。

```
pyinstaller --onefile --windowed --add-data "assets:assets" src/main.py
```

---
Copyright © 2025 pantsman, ISSA-Motomu, tanosou, osato03, nagata
