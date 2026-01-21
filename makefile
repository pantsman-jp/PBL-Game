.PHONY: build

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
