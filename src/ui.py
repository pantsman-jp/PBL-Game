"""
簡易ウィンドウ描画 | src/ui.py
会話ウィンドウを作成
"""

import pygame


def draw_window(
    surface,
    font,
    lines,
    rect=(48, 320, 544, 128),
    bgcolor=(0, 0, 0),
    fg=(255, 255, 255),
):
    """
    画面下部にテキストウィンドウを表示します．
    rect: (x, y, w, h)
    """
    x, y, w, h = rect
    pygame.draw.rect(surface, bgcolor, (x, y, w, h))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 2)
    line_h = font.get_linesize()
    for i, line in enumerate(lines):
        surf = font.render(line, True, fg)
        surface.blit(surf, (x + 8, y + 8 + i * line_h))


def draw_objective_bar(
    surface, font, text, rect=(0, 0, 900, 30), bgcolor=(0, 0, 100), fg=(255, 255, 200)
):
    """
    画面上部または指定位置に目標テキストバーを表示します
    """
    x, y, w, h = rect
    # 半透明の背景などを入れたければSurfaceを使うが、ここではシンプルに矩形描画
    pygame.draw.rect(surface, bgcolor, rect)
    pygame.draw.line(surface, (255, 255, 255), (x, y + h), (x + w, y + h), 2)

    text_surf = font.render(text, True, fg)
    # 中央揃えのような配置
    dest_x = x + 10
    dest_y = y + (h - text_surf.get_height()) // 2
    surface.blit(text_surf, (dest_x, dest_y))
