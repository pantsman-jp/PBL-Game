from PIL import Image
import json

# !!!!!!!実行はルート直下で!!!!!!!

IMAGE_PATH = "assets/img/world_map.png"
TILE_SIZE = 16


def is_sea_color(r, g, b):
    return b > r and b > g and b > 100


def is_sea_tile(pixels, width, height, tx, ty):
    """
    注目画素とその8近傍で、海か陸かを投票し、
    多数決で決定する。
    """
    cx = tx * TILE_SIZE + TILE_SIZE // 2
    cy = ty * TILE_SIZE + TILE_SIZE // 2
    sea_count = 0
    total = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            px = cx + dx
            py = cy + dy
            if px < 0 or py < 0 or px >= width or py >= height:
                continue
            r, g, b = pixels[px, py]
            total += 1
            if is_sea_color(r, g, b):
                sea_count += 1
    return sea_count * 2 >= total


def main():
    try:
        img = Image.open(IMAGE_PATH)
    except FileNotFoundError:
        print(f"エラー: {IMAGE_PATH} が見つかりません。")
        return
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size
    cols = width // TILE_SIZE
    rows = height // TILE_SIZE
    map_grid = [[False for _ in range(cols)] for _ in range(rows)]
    for y in range(rows):
        for x in range(cols):
            map_grid[y][x] = is_sea_tile(pixels, width, height, x, y)
    walls = []
    for y in range(rows):
        for x in range(cols):
            if not map_grid[y][x]:
                continue
            is_coast = False
            if y > 0 and not map_grid[y - 1][x]:
                is_coast = True
            elif y < rows - 1 and not map_grid[y + 1][x]:
                is_coast = True
            elif x > 0 and not map_grid[y][x - 1]:
                is_coast = True
            elif x < cols - 1 and not map_grid[y][x + 1]:
                is_coast = True
            if is_coast:
                walls.append([x, y])
    with open("assets/data/walls_output.txt", "w") as f:
        f.write(json.dumps(walls))
    print("Done")


if __name__ == "__main__":
    main()
