import pygame
import sys
import os
import re
from level_data import levels

pygame.init()

screen_width = 1500
screen_height = 960
tile_size = 32

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Map Maker")
clock = pygame.time.Clock()

cols, rows = 15, 15
offset_x = 340
offset_y = (screen_height - rows * tile_size) // 2

# -------------------
# Level laden
# -------------------
print(f"Es gibt {len(levels)} Level.")
while True:
    try:
        level_index = input(f"Wähle ein Level zum Laden (0-{len(levels)-1}) oder drücke Enter für leeres Level: ")
        if level_index == "":
            world_data = [[0 for _ in range(cols)] for _ in range(rows)]
            break
        level_index = int(level_index)
        if 0 <= level_index < len(levels):
            world_data = [row[:] for row in levels[level_index]]  # Kopie des Levels
            break
        else:
            print("Ungültiger Index!")
    except ValueError:
        print("Bitte eine Zahl eingeben!")

print("Level erfolgreich geladen!")

# -------------------
# Tiles Palette
# -------------------
class TilesPalette:
    def __init__(self, tile_folder, tiles_per_column=30, start_col=36):
        self.tile_list = []
        self.tile_rects = []
        self.selected_index = None

        if not os.path.isdir(tile_folder):
            print("Tile-Ordner nicht gefunden:", tile_folder)
            return

        tile_images = []
        for filename in sorted(os.listdir(tile_folder)):
            if filename.endswith(".png"):
                path = os.path.join(tile_folder, filename)
                tile_images.append(pygame.image.load(path).convert_alpha())

        row_count = 0
        col_count = start_col
        tile_index = 0
        for tile in tile_images:
            img = pygame.transform.scale(tile, (tile_size, tile_size))
            img_rect = img.get_rect()
            img_rect.x = col_count * tile_size
            img_rect.y = row_count * tile_size

            self.tile_list.append((img, img_rect))
            self.tile_rects.append((tile_index, img_rect))

            tile_index += 1
            row_count += 1
            if row_count >= tiles_per_column:
                row_count = 0
                col_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (0, 0, 0), tile[1], 1)

        if self.selected_index is not None:
            for idx, rect in self.tile_rects:
                if idx == self.selected_index:
                    pygame.draw.rect(screen, (255, 0, 0), rect, 3)
                    break

    def handle_mouse_click(self, pos):
        for idx, rect in self.tile_rects:
            if rect.collidepoint(pos):
                self.selected_index = idx
                print("Selected tile:", idx + 1)
                break

# -------------------
# Map zum Anzeigen
# -------------------
class Map:
    def draw(self):
        for y in range(rows):
            for x in range(cols):
                tile_id = world_data[y][x]
                if 0 < tile_id <= len(palette.tile_list):
                    tile_img = palette.tile_list[tile_id - 1][0]
                    screen.blit(tile_img, (offset_x + x * tile_size, offset_y + y * tile_size))

        # Gitterlinien
        for y in range(rows + 1):
            pygame.draw.line(screen, (200, 200, 200),
                             (offset_x, offset_y + y * tile_size),
                             (offset_x + cols * tile_size, offset_y + y * tile_size))
        for x in range(cols + 1):
            pygame.draw.line(screen, (200, 200, 200),
                             (offset_x + x * tile_size, offset_y),
                             (offset_x + x * tile_size, offset_y + rows * tile_size))


tile_folder = "Sprites/Tiles/Default"
palette = TilesPalette(tile_folder)
tiles_map = Map()
palette_rect = pygame.Rect(36 * tile_size, 0, screen_width - 36 * tile_size, screen_height)

# -------------------
# Level speichern (direkt in level_data.py)
# -------------------
def save_level():
    filename = "level_data.py"

    # Datei erstellen, falls sie nicht existiert
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("levels = []\n\n")

    # Bestehenden Inhalt lesen
    with open(filename, "r") as f:
        content = f.read()

    # Nächste Level-Nummer bestimmen
    existing_nums = [int(n) for n in re.findall(r"level_(\d+)", content)]
    next_num = max(existing_nums) + 1 if existing_nums else 1

    level_var = f"level_{next_num}"
    new_level = f"{level_var} = [\n"
    for row in world_data:
        new_level += "    " + str(row) + ",\n"
    new_level += "]\nlevels.append(" + level_var + ")\n\n"

    # Neues Level anhängen
    with open(filename, "a") as f:
        f.write(new_level)

    print(f"Level gespeichert als '{level_var}' und zu levels hinzugefügt.")

# -------------------
# Hauptloop
# -------------------
running = True
while running:
    clock.tick(60)
    screen.fill((255, 255, 255))

    palette.draw()
    tiles_map.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_level()
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Drücke 'S', um jederzeit zu speichern
                save_level()
            elif event.key == pygame.K_r:  # Clear: Alles löschen
                world_data = [[0 for _ in range(cols)] for _ in range(rows)]
                print("Level geleert!")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if palette_rect.collidepoint(event.pos):
                palette.handle_mouse_click(event.pos)
            else:
                mouse_x, mouse_y = event.pos
                grid_x = (mouse_x - offset_x) // tile_size
                grid_y = (mouse_y - offset_y) // tile_size

                if 0 <= grid_x < cols and 0 <= grid_y < rows:
                    if event.button == 1 and palette.selected_index is not None:
                        world_data[grid_y][grid_x] = palette.selected_index + 1
                    elif event.button == 3:
                        world_data[grid_y][grid_x] = 0

    pygame.display.update()

pygame.quit()
sys.exit()