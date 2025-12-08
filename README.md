# PBL-Game

## 概要
このゲームは、**宇宙工学・宇宙理学の面白さを高校生に紹介する** というコンセプトで開発されています。

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
`Pyinstaller` が必要。以下でインストール。

```
pip install pyinstaller
```

`PBL-Game` 直下で以下を実行。

```
pyinstaller --onefile --windowed --add-data "assets;assets" src\main.py
```

`dist/main.exe` が生成される。

---
Copyright © 2025 pantsman, ISSA-Motomu, tanosou, osato03, nagata