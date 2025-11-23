import pygame
import os

pygame.init()

SCREEN_WIDTH = 15 * 64
SCREEN_HEIGHT = 15 * 64
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer mit 15x15 World")
tile_folder = "Sprites/Tiles/Default"

clock = pygame.time.Clock()

TILE_SIZE = 64

world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 118, 0, 62, 0, 0, 0, 0, 0, 49, 0],
    [0, 0, 0, 0, 0, 179, 180, 180, 181, 0, 0, 0, 184, 183, 185],
    [0, 0, 0, 0, 0, 0, 37, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 167, 0, 0, 0, 0, 37, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 45, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 179, 180, 180, 180, 181, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 177, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 177],
    [0, 0, 0, 0, 0, 0, 0, 37, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 37, 0, 37, 0, 0, 0, 0, 177, 0],
    [62, 0, 0, 116, 125, 128, 0, 0, 0, 0, 116, 0, 0, 62, 0],
    [175, 174, 174, 174, 174, 176, 312, 312, 312, 175, 174, 174, 174, 174, 176],
    [172, 171, 171, 171, 171, 173, 310, 310, 310, 172, 171, 171, 171, 171, 173],
    [172, 171, 171, 171, 171, 173, 310, 310, 310, 172, 171, 171, 171, 171, 173],
]

class World:
    def __init__(self, data):
        self.tile_list = []

        self.tile_images = []
        for filename in sorted(os.listdir(tile_folder)):
            if filename.endswith(".png"):
                path = os.path.join(tile_folder, filename)
                img = pygame.image.load(path).convert_alpha()
                self.tile_images.append(img)

        row_count = 0
        for row in data:
            col_count = 0
            for tile_id in row:
                if 0 < tile_id <= len(self.tile_images):
                    raw_img = self.tile_images[tile_id - 1]
                    img = pygame.transform.scale(raw_img, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect(topleft=(col_count * TILE_SIZE, row_count * TILE_SIZE))
                    self.tile_list.append((img, img_rect))
                col_count += 1
            row_count += 1

    def draw(self):
        for img, img_rect in self.tile_list:
            screen.blit(img, img_rect)

world = World(world_data)

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((135, 206, 235))

    world.draw()

    pygame.display.flip()

pygame.quit()
