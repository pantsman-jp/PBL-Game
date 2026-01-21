# git 操作
git checkout main
git pull

# pyinstaller 実行
pyinstaller --onefile --windowed --add-data "assets;assets" src\main.py

# 出力先フォルダ作成
$dest = "..\for-win"
if (-Not (Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest
}

# 既存ファイル削除（上書き対応）
Remove-Item -Path "$dest\main.exe" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$dest\LICENSE.txt" -Force -ErrorAction SilentlyContinue

# main.exe コピー
Copy-Item -Path ".\dist\main.exe" -Destination $dest

# LICENSE コピー（名前を LICENSE.txt に変更）
Copy-Item -Path ".\LICENSE" -Destination "$dest\LICENSE.txt"

# zip 圧縮
$zipPath = "..\for-win.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

# for-win フォルダ自体を圧縮
Compress-Archive -Path $dest -DestinationPath $zipPath