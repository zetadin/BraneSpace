import sys
import pygame
from pygame.locals import *

import numpy as np


pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

HEIGHT = 600
WIDTH = 600
FPS = 60

SIM_SIZE = 32


FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BraneSpace")

# font
pygame.font.init()
serif_font = pygame.font.SysFont('liberationserif', 18)

# game object lists
all_sprites = pygame.sprite.Group()
updatable_sprites = pygame.sprite.Group()


class Brane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.amplitude = np.random.random((SIM_SIZE, SIM_SIZE))
        self.surf = pygame.Surface((2, 2)) # temporary
        self.surf.fill((128,128,128))
        self.rect = pygame.Rect(0,0,WIDTH,WIDTH)
        
    def register(self):
        # put into game object lists
        all_sprites.add(self)
        updatable_sprites.add(self)
        
        
    def update(self, dt):
        # re-paint the surface
        amp_arr = np.floor(255*self.amplitude/np.max(self.amplitude)).astype(np.uint8)
        amp_arr = np.repeat(amp_arr[:, :, np.newaxis], 3, axis=2)
        amp_surf = pygame.surfarray.make_surface(amp_arr)
        self.surf = pygame.transform.smoothscale(amp_surf, (WIDTH,WIDTH))
        
        
        
# init objects        
cur_brane = Brane()
cur_brane.register()


# initial guess at frame time
dt = 1000./FPS

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
    # update objects
    for entity in updatable_sprites:
        entity.update(dt)
     
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
    dt = FramePerSec.tick(FPS)
    
    