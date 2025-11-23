import pygame
import os

pygame.init()

SCREEN_WIDTH = 15 * 64
SCREEN_HEIGHT = 15 * 64
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python Platformer")
tile_folder = "Sprites/Tiles/Default"

clock = pygame.time.Clock()

TILE_SIZE = 64

world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 182, 183, 186, 0, 0, 0, 0, 182, 183, 186, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 167, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [175, 174, 174, 174, 174, 174, 174, 174, 174, 174, 174, 174, 174, 174, 176],
    [172, 171, 171, 171, 171, 171, 171, 171, 171, 171, 171, 171, 171, 171, 173],
    [169, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 170],
]
class Player:
    def __init__(self, x, y):
        raw_img = pygame.image.load("Sprites/Characters/Default/character_green_1.png")
        visible = raw_img.get_bounding_rect()
        cropped = raw_img.subsurface(visible)
        scaled = pygame.transform.scale_by(cropped, 1)

        self.image = scaled
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = 5
        self.vel_y = 0
        self.in_air = True
        self.jumped = False

    def update(self):
        dx = 0
        dy = 0

        key = pygame.key.get_pressed()
        # horizonal movement
        if key[pygame.K_RIGHT]:
            dx += self.speed
        if key[pygame.K_LEFT]:
            dx -= self.speed
        # jumped
        if key[pygame.K_UP]:
            if not self.jumped and not self.in_air:
                self.vel_y = -15
                self.jumped = True
        else:
            self.jumped = False

        # gravity
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # collision detection with tiles
        self.in_air = True
        for tile in world.tile_list:
            # check for collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # check for collision in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # check if below th ground
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                # check if above the ground
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


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
            pygame.draw.rect(screen, (0, 255, 0), img_rect, 2)

world = World(world_data)
player = Player(55, 672)

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((135, 206, 235))

    world.draw()
    player.update()

    pygame.display.flip()

pygame.quit()
