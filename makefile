.PHONY: build, sc

build:
	git checkout main
	git pull
	. .venv/bin/activate && pyinstaller src/main.py --windowed --onedir --add-data "assets:assets" --noconfirm
	mkdir -p ../for-mac
	rm -rf ../for-mac/main.app
	cp -R dist/main.app ../for-mac/
	cp LICENSE ../for-mac/LICENSE.txt
	rm -f ../for-mac.zip
	cd .. && zip -r for-mac.zip for-mac

# "sc" means "show-count"
sc:
	@curl -s https://api.github.com/repos/pantsman-jp/PBL-Game/releases \
	| tr ',' '\n' \
	| grep -E '"name": "(for-win.zip|for-mac.zip)"|"download_count"' \
	| paste - - \
	| sed -E 's/.*"name": "([^"]+)".*"download_count": ([0-9]+)/\1: \2/'