import sys
import pygame
from pygame.locals import *

pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

HEIGHT = 600
WIDTH = 600
ACC = 0.5
FRIC = -0.12
FPS = 60

FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BraneSpace")

# font
pygame.font.init()
serif_font = pygame.font.SysFont('liberationserif', 18)

class Brane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.surf = pygame.Surface((512, 512))
        self.surf.fill((128,128,128))
        self.rect = self.surf.get_rect(center = (WIDTH/2, WIDTH/2))
        
cur_brane = Brane()

all_sprites = pygame.sprite.Group()
all_sprites.add(cur_brane)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
     
    # wipe screen 
    displaysurface.fill((0,0,0))
 
    # draw everything
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
 
    # show FPS
    fps_surface = serif_font.render(
            f"FPS: {FramePerSec.get_fps():.0f}",
            False, (180, 255, 150)
            )
    displaysurface.blit(fps_surface, (5,5))
    
    # push to frame buffer
    pygame.display.update()
    
    # wait for next frame
    FramePerSec.tick(FPS)
    
    