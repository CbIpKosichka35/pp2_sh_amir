import pygame
import sys
import random
import time
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 400, 600
SPEED = 5
SCORE = 0
COINS = 0

DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Verdana", 20)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.Surface((40, 70))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, WIDTH-40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > HEIGHT):
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, WIDTH-40), 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        self.rect.center = (random.randint(30, WIDTH-30), -50)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > HEIGHT):
            self.spawn()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.Surface((40, 70))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
       
    def move(self):
        keys = pygame.key.get_pressed()
        if self.rect.left > 0 and keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < WIDTH and keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies = pygame.sprite.Group(E1)
coins = pygame.sprite.Group(C1)
all_sprites = pygame.sprite.Group(P1, E1, C1)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.fill((255, 255, 255))
    
    s_text = font_small.render(f"Enemies: {SCORE}", True, (0,0,0))
    c_text = font_small.render(f"Coins: {COINS}", True, (0,0,0))
    DISPLAYSURF.blit(s_text, (10, 10))
    DISPLAYSURF.blit(c_text, (WIDTH - 100, 10))

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    if pygame.sprite.spritecollide(P1, coins, False):
        COINS += 1
        C1.spawn()

    if pygame.sprite.spritecollideany(P1, enemies):
        time.sleep(1)
        pygame.quit()
        sys.exit()        
        
    pygame.display.update()
    clock.tick(60)