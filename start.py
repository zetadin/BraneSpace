import sys
import pygame
from pygame.locals import *

import numpy as np
import numpy.typing as npt


from Brane import Brane
from Universe import updatables, drawables
from View import View, HEIGHT, WIDTH, FPS
from entities.Entity import SpriteEntity
from entities.SimpleObjects import Ball
from entities.structures.Portal import Portal
from entities.Player import Player


view = View()

        
# init objects in universe
cur_brane = Brane()
cur_brane.register()

ball = Ball()
ball.register(cur_brane)

player = Player()
player.register(cur_brane)

portal = Portal()
portal.register(cur_brane)

filler = SpriteEntity()
filler.r = np.array([5,5])
filler.register(cur_brane)


# initial guess at frame time
dt = 1000./FPS


#
## fast forward
#for entity in updatable_sprites:
#    entity.update(2500)
    



# game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
    # update objects
    for entity in updatable_sprites:
        entity.update(dt)
     
    # wipe screen 
    view.displaysurface.fill((0,0,0))
 
    # draw everything
    for entity in all_sprites:
        entity.draw(view.displaysurface)
 
    # show FPS
    fps_surface = view.serif_font.render(
            f"FPS: {view.FramePerSec.get_fps():.0f}",
            False, (180, 255, 150)
            )
    view.displaysurface.blit(fps_surface, (5,5))
    
    # push to frame buffer
    pygame.display.update()
    
    # wait for next frame
    dt = view.FramePerSec.tick(FPS)
    
#    if(cur_brane.elapsed>80):
#        sys.exit()
    
    