import pygame
import sys
import os
from level_data import *

pygame.init()

screen_width = 960
screen_height = 960

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pixel Platformer")
clock = pygame.time.Clock()

# Game variables
start_pos = (55, 672)  # Player start position for each level
tile_size = 64
level = 0  # Current level index

# Game groups for special objects
special_tile_group = pygame.sprite.Group()

# Load sound effects and background music
jump_sound = pygame.mixer.Sound("Sounds/sfx_jump.ogg")
trampoline_jump_sound = pygame.mixer.Sound("Sounds/sfx_jump-high.ogg")
coin_select_sound = pygame.mixer.Sound("Sounds/sfx_coin.ogg")
spike_damaged = pygame.mixer.Sound("Sounds/sfx_disappear.ogg")
pygame.mixer.music.load("Sounds/background_music.ogg")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)  # Loop background music

# Load background image
tree_background = pygame.image.load("Sprites/Backgrounds/Default/background_clouds.png")
tree_background = pygame.transform.scale(tree_background, (960, 960))

# Preload all tile images once for performance
tile_images = []
tile_folder = "Sprites/Tiles/Default"
for filename in sorted(os.listdir(tile_folder)):
    if filename.endswith(".png"):
        path = os.path.join(tile_folder, filename)
        tile_images.append(pygame.image.load(path).convert_alpha())

def get_collision_rect(raw_img, img_rect):
    """
    Returns the collision rectangle based on the visible part of the image.
    Scales the bounding box to match the display size of the tile.
    """
    visible = raw_img.get_bounding_rect()
    scale_x = tile_size / raw_img.get_width()
    scale_y = tile_size / raw_img.get_height()
    return pygame.Rect(
        img_rect.x + visible.x * scale_x,
        img_rect.y + visible.y * scale_y,
        visible.width * scale_x,
        visible.height * scale_y
    )


class Player:
    def __init__(self, x, y):
        # Load player animation frames (right and left)
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0

        for num in range(1, 5):
            raw_img = pygame.image.load(f'Sprites/Characters/Default/character_green_{num}.png').convert_alpha()
            visible = raw_img.get_bounding_rect()
            cropped = raw_img.subsurface(visible)
            scaled = pygame.transform.scale_by(cropped, 1)
            self.images_right.append(scaled)
            self.images_left.append(pygame.transform.flip(scaled, True, False))

        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Narrower and shorter collision rect (50x80), centered inside the body
        self.coll_rect = pygame.Rect(x + 10, y + 10, 50, 80)

        self.speed = 10
        self.vel_y = 0
        self.in_air = True
        self.jumped = False
        self.direction = 1  # 1 = right, -1 = left

    def update(self, level_index):
        dx = 0
        dy = 0
        walk_countdown = 5  # Frame delay between animation changes

        key = pygame.key.get_pressed()
        # Horizontal movement
        if key[pygame.K_RIGHT]:
            dx += 5
            self.counter += 1
            self.direction = 1
        if key[pygame.K_LEFT]:
            dx -= 5
            self.counter += 1
            self.direction = -1

        # Jumping
        if key[pygame.K_UP]:
            if not self.jumped and not self.in_air:
                jump_sound.play()
                self.vel_y = -15
                self.jumped = True
        else:
            self.jumped = False

        # Reset animation if not moving
        if not key[pygame.K_RIGHT] and not key[pygame.K_LEFT]:
            self.counter = 0
            self.index = 0
        # If pressing both directions, stop animation
        if key[pygame.K_RIGHT] and key[pygame.K_LEFT]:
            self.counter = 0
            self.index = 0

        # Walking animation frame control
        if self.counter > walk_countdown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0

        # Select correct image based on direction
        img_list = self.images_right if self.direction == 1 else self.images_left
        self.image = img_list[self.index]

        # Gravity
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Collision detection with solid tiles
        self.in_air = True
        for tile_img, tile_rect, coll_rect, tile_gid in world.tile_list:
            if tile_gid not in world.solid_gid_set:
                continue
            # Horizontal collision
            if coll_rect.colliderect(self.coll_rect.x + dx, self.coll_rect.y, self.coll_rect.width, self.coll_rect.height):
                dx = 0
            # Vertical collision
            if coll_rect.colliderect(self.coll_rect.x, self.coll_rect.y + dy, self.coll_rect.width, self.coll_rect.height):
                if self.vel_y < 0:  # Hitting head
                    dy = coll_rect.bottom - self.coll_rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:  # Landing
                    dy = coll_rect.top - self.coll_rect.bottom
                    self.in_air = False

        # Collision with special tiles (objects)
        for special_tile in special_tile_group:
            if special_tile.coll_rect.colliderect(self.coll_rect):
                if isinstance(special_tile, Trampoline):
                    # Bounce only when falling and hitting the top
                    if self.vel_y >= 0 and self.coll_rect.bottom <= special_tile.coll_rect.top + 10:
                        self.vel_y = -20
                        self.in_air = True
                        trampoline_jump_sound.play()
                elif isinstance(special_tile, Spikes):
                    spike_damaged.play()
                    # Reset player to start position
                    self.rect.topleft = (55, 672)
                    self.coll_rect.topleft = (55 + 10, 672 + 10)
                    self.vel_y = 0
                elif isinstance(special_tile, Coin):
                    coin_select_sound.play()
                    special_tile.kill()  # Remove the coin
                elif isinstance(special_tile, Flag):
                    # Level complete, move to next
                    self.rect.topleft = (55, 672)
                    self.coll_rect.topleft = (55 + 10, 672 + 10)
                    level_index += 1

        # Apply movement
        self.rect.x += dx
        self.rect.y += dy
        self.coll_rect.x += dx
        self.coll_rect.y += dy

        # Prevent leaving the left/right screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.coll_rect.left = self.rect.left + 10
        elif self.rect.right > screen_width:
            self.rect.right = screen_width
            self.coll_rect.right = self.rect.right - 10

        # Draw player
        screen.blit(self.image, self.rect)
        # Debug collision box:
        # pygame.draw.rect(screen, (255, 0, 0), self.coll_rect, 2)

        # Reset player if falling out of the screen
        if self.rect.top > screen_height:
            self.rect.topleft = (55, 672)
            self.coll_rect.topleft = (55 + 10, 672 + 10)
            self.vel_y = 0

        return level_index


class SpecialTile(pygame.sprite.Sprite):
    def __init__(self, x, y, raw_img):
        super().__init__()
        self.image = pygame.transform.scale(raw_img, (tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coll_rect = get_collision_rect(raw_img, self.rect)

# Special tile classes (no extra logic yet)
class Trampoline(SpecialTile): pass
class Spikes(SpecialTile): pass
class Coin(SpecialTile): pass
class Flag(SpecialTile): pass


class World:
    def __init__(self, data):
        self.tile_list = []  # Stores (image, image rect, collision rect, tile ID)
        # Mapping of special tile IDs to their classes
        special_gid_to_class = {
            128: Trampoline,
            127: Spikes,
            12: Spikes,
            121: Spikes,
            105: Spikes,
            106: Spikes,
            107: Spikes,
            310: Spikes,
            311: Spikes,
            312: Spikes,
            308: Spikes,
            58: Coin,
            59: Coin,
            60: Coin,
            37: Coin,
            80: Coin,
            35: Coin,
            61: Coin,
            49: Flag,
            50: Flag
        }

        # Set of tile IDs that are solid (blocking movement)
        self.solid_gid_set = {
            1, 17, 142, 157, 177, 225, 241, 261, 280, 295,
            2, 18, 143, 158, 178,220,221, 226, 242, 262, 281, 296,
            3, 19, 144, 164, 179, 227, 248, 263, 282, 297,
            4, 20, 145, 165, 180, 228, 249, 264, 283, 298,
            5, 21, 146, 166, 181, 229, 250, 265, 284, 304,
            6, 28, 147, 167, 182, 230, 251, 266, 285, 305,
            7, 29, 148, 168, 183, 231, 252, 267, 286, 306,
            8, 41, 149, 169, 184, 232, 253, 268, 287, 313,
            9, 111, 150, 170, 185, 233, 254, 269, 288, 31,
            10, 112, 151, 171, 186, 234, 255, 270, 289,
            11, 113, 152, 172, 192, 235, 256, 276, 290,
            13, 114, 153, 173, 193, 236, 257, 277, 291,
            14, 139, 154, 174, 194, 237, 258, 278, 292,
            15, 140, 155, 175, 223, 238, 259, 314, 293,
            16, 141, 156, 176, 224, 240, 260, 279, 294,
        }

        # Loop through the level data and create tiles
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                x = col_count * tile_size
                y = row_count * tile_size

                if tile <= 0:
                    # Empty space, skip
                    col_count += 1
                    continue

                if tile > len(tile_images):
                    print(f"Error at Tile-ID {tile} at row: {row_count}, col: {col_count}")
                    col_count += 1
                    continue

                raw_img = tile_images[tile - 1]

                # Special objects
                if tile in special_gid_to_class:
                    cls = special_gid_to_class[tile]
                    obj = cls(x, y, raw_img)
                    special_tile_group.add(obj)

                else:
                    # Normal tile (with or without collision)
                    img = pygame.transform.scale(raw_img, (tile_size, tile_size))
                    img_rect = img.get_rect(topleft=(x, y))

                    if tile in self.solid_gid_set:
                        coll_rect = get_collision_rect(raw_img, img_rect)
                    else:
                        # Decorative tile, no collision
                        coll_rect = pygame.Rect(0, 0, 0, 0)

                    self.tile_list.append((img, img_rect, coll_rect, tile))

                col_count += 1
            row_count += 1

    def draw(self):
        # Draw all tiles in the world
        for tile_img, tile_rect, coll_rect, _ in self.tile_list:
            screen.blit(tile_img, tile_rect)


# Create the first world and player
world = World(levels[level])
player = Player(*start_pos)

# Main game loop
running = True
while running:
    clock.tick(60)  # Limit FPS to 60
    screen.blit(tree_background, (0, 0))
    world.draw()
    special_tile_group.draw(screen)

    new_level = player.update(level)

    # Check for level change
    if new_level != level and new_level < len(levels):
        level = new_level
        special_tile_group.empty()
        world = World(levels[level])
        player.rect.topleft = (55, 672)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()
sys.exit()