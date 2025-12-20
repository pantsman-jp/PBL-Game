from PIL import Image
import json

####################
# 実行はルート直下で #
####################

IMAGE_PATH = "assets/img/world_map.png"
TILE_SIZE = 16
FOOT_OFFSET_Y = 2


def is_sea_color(r, g, b):
    return b > r and b > g and b > 100


def vote_sea(pixels, width, height, samples):
    sea_score = 0
    land_score = 0
    for x, y, w in samples:
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        r, g, b = pixels[x, y]
        if is_sea_color(r, g, b):
            sea_score += w
        else:
            land_score += w
    return sea_score >= land_score


def is_sea_tile_player_based(pixels, width, height, tx, ty):
    base_x = tx * TILE_SIZE + TILE_SIZE // 2
    base_y = (ty + 1) * TILE_SIZE - FOOT_OFFSET_Y
    samples = [
        (base_x, base_y, 3),
        (base_x - 2, base_y, 2),
        (base_x + 2, base_y, 2),
        (base_x, base_y - 2, 2),
        (base_x - 2, base_y - 2, 1),
        (base_x + 2, base_y - 2, 1),
    ]
    return vote_sea(pixels, width, height, samples)


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
            map_grid[y][x] = is_sea_tile_player_based(pixels, width, height, x, y)
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
