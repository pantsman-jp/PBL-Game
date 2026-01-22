function build {
    git checkout main
    git pull
    pyinstaller --onefile --windowed --add-data "assets;assets" src\main.py
    $dest = "..\for-win"
    if (-Not (Test-Path $dest)) {
        New-Item -ItemType Directory -Path $dest | Out-Null
    }
    Remove-Item "$dest\main.exe" -Force -ErrorAction SilentlyContinue
    Remove-Item "$dest\LICENSE.txt" -Force -ErrorAction SilentlyContinue
    Copy-Item ".\dist\main.exe" -Destination $dest
    Copy-Item ".\LICENSE" -Destination "$dest\LICENSE.txt"
    $zipPath = "..\for-win.zip"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    Compress-Archive -Path $dest -DestinationPath $zipPath
}

# "sc" means "show-count"
function sc {
    $url = "https://api.github.com/repos/pantsman-jp/PBL-Game/releases"
    $releases = Invoke-RestMethod -Uri $url -Method Get
    $assets = $releases[0].assets
    $assets |
        Where-Object { $_.name -eq "for-win.zip" -or $_.name -eq "for-mac.zip" } |
        ForEach-Object {
            "{0}: {1}" -f $_.name, $_.download_count
        }
}