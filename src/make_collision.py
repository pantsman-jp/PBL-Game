from PIL import Image
import json

# 画像パス（保存したファイル名に合わせてください）
IMAGE_PATH = "assets/img/world_map.png"
TILE_SIZE = 16


def is_sea(r, g, b):
    """色が海かどうかを判定する"""
    # 青成分(B)が強く、緑(G)より大きい場合は「海」とみなす
    return b > r and b > g and b > 100


def main():
    try:
        img = Image.open(IMAGE_PATH)
    except FileNotFoundError:
        print(f"エラー: {IMAGE_PATH} が見つかりません。画像を配置してください。")
        return

    width, height = img.size
    print(f"画像サイズ: {width}x{height}")

    # RGBモードに変換
    img = img.convert("RGB")
    pixels = img.load()

    cols = width // TILE_SIZE
    rows = height // TILE_SIZE

    # ステップ1: まず全てのタイルのタイプ（海か陸か）を判定してメモリに保持する
    # True = 海, False = 陸
    map_grid = [[False for _ in range(cols)] for _ in range(rows)]

    print("マップ解析中...")
    for y in range(rows):
        for x in range(cols):
            px = x * TILE_SIZE + TILE_SIZE // 2
            py = y * TILE_SIZE + TILE_SIZE // 2

            if px >= width or py >= height:
                continue

            r, g, b = pixels[px, py]
            if is_sea(r, g, b):
                map_grid[y][x] = True

    # ステップ2: 境界線（海岸）だけを抽出する
    walls = []
    print("境界線抽出中...")

    for y in range(rows):
        for x in range(cols):
            # 自分が「陸」なら壁ではないのでスキップ
            if not map_grid[y][x]:
                continue

            # 自分が「海」の場合、周囲4方向をチェック
            # 上下左右のどこかに「陸(False)」があれば、ここは海岸線（必要な壁）
            is_coast = False

            # 上をチェック
            if y > 0 and not map_grid[y - 1][x]:
                is_coast = True
            # 下をチェック
            elif y < rows - 1 and not map_grid[y + 1][x]:
                is_coast = True
            # 左をチェック
            elif x > 0 and not map_grid[y][x - 1]:
                is_coast = True
            # 右をチェック
            elif x < cols - 1 and not map_grid[y][x + 1]:
                is_coast = True

            # 境界線であればリストに追加
            if is_coast:
                walls.append([x, y])

    print(f"壁（海岸線）の数: {len(walls)}")

    # ファイルに保存
    output_file = "walls_output.txt"
    with open(output_file, "w") as f:
        f.write(json.dumps(walls))

    print(
        f"結果を {output_file} に保存しました。このファイルの中身をコピーしてください。"
    )


if __name__ == "__main__":
    main()
