"""
UI描画ユーティリティ | src/ui.py
テキストウィンドウや目標バーなどの共通UI部品の描画を提供
"""

import pygame

# --- デフォルト設定 ---
DEFAULT_PADDING = 12
WINDOW_BORDER_COLOR = (200, 200, 200)
WINDOW_BORDER_WIDTH = 2


def draw_window(
    surface,
    font,
    lines,
    rect=(48, 320, 544, 128),
    bgcolor=(0, 0, 0),
    fg=(255, 255, 255),
    alpha=200,
):
    """
    指定された範囲にテキストウィンドウを描画します。
    背後を透過させるために一時的なSurfaceを使用します。
    """
    x, y, w, h = rect

    # 1. ウィンドウ本体の描画（半透明対応）
    window_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    window_surf.fill((*bgcolor, alpha))
    surface.blit(window_surf, (x, y))

    # 2. 枠線の描画
    pygame.draw.rect(surface, WINDOW_BORDER_COLOR, (x, y, w, h), WINDOW_BORDER_WIDTH)

    # 3. テキストの描画
    line_h = font.get_linesize()
    for i, line in enumerate(lines):
        if not line:
            continue

        text_surf = font.render(line, True, fg)
        # 指定座標からパディング分ずらして描画
        dest_pos = (x + DEFAULT_PADDING, y + DEFAULT_PADDING + i * line_h)
        surface.blit(text_surf, dest_pos)


def draw_objective_bar(
    surface, font, text, rect=(0, 0, 900, 32), bgcolor=(20, 20, 60), fg=(255, 255, 200)
):
    """
    画面上部に目標（クエスト内容）を表示するバーを描画します。
    """
    x, y, w, h = rect

    # 背景の描画
    pygame.draw.rect(surface, bgcolor, rect)

    # 下部のセパレータ線
    line_color = (255, 255, 255)
    pygame.draw.line(surface, line_color, (x, y + h - 1), (x + w, y + h - 1), 1)

    # テキストの描画（垂直中央揃え）
    if text:
        text_surf = font.render(text, True, fg)

        # 垂直方向の中央座標を計算
        text_y = y + (h - text_surf.get_height()) // 2
        # 左端から少し余白を空けて描画
        surface.blit(text_surf, (x + 15, text_y))
