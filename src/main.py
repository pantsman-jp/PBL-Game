"""
メインエントリポイント | src/main.py
OS ごとの音声初期化を行い、App を起動する
"""

import os
import sys
import traceback
import pygame
from src.app import App


def init_audio():
    """
    OS 毎に音声を初期化
    """
    try:
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.init()
        return
    except Exception:
        pygame.quit()
    if sys.platform.startswith("win"):
        os.environ["SDL_AUDIODRIVER"] = "directsound"
    elif sys.platform == "darwin":
        os.environ["SDL_AUDIODRIVER"] = "coreaudio"
    else:
        os.environ["SDL_AUDIODRIVER"] = "pulseaudio"
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()


def main():
    init_audio()
    app = App()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
