import sys
import pygame
from pygame.locals import *

import numpy as np


from Brane import Brane
from View import View, HEIGHT, WIDTH, FPS
from entities.Entity import SpriteEntity
from entities.SimpleObjects import Ball
from entities.structures.Portal import Portal
from entities.Player import Player
from Universe import updatables, drawables
from UI.TopBar import TopBar


view = View()

# init UI
tb = TopBar(view)

        
# init objects in universe
cur_brane = Brane()
cur_brane.register()

for i in range(100):
    ball = Ball()
#    ball.r = np.array([WIDTH*0.5, WIDTH*0.5])
    ball.r = np.random.random(2)*WIDTH
    ball.v = (np.random.random(2) - 0.5)*0.2
    ball.register(cur_brane)

player = Player()
player.register(cur_brane)
tb.bindPlayer(player)

portal = Portal()
portal.r = np.array([WIDTH*0.7, WIDTH*0.7])
portal.register(cur_brane)

filler = SpriteEntity()
filler.r = np.array([115.,215.])
filler.register(cur_brane)

# initial guess at frame time
dt = 1000./FPS


# game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
    # update objects
    for entity in updatables:
        entity.update(dt)
     
    # wipe screen 
    view.displaysurface.fill((0,0,0))
 
    # draw everything
    for entity in drawables:
        entity.draw(view)
        
        
    # draw the UI
    tb.draw(view)
 
    # push to frame buffer
    pygame.display.update()
    
    # wait for next frame
    dt = view.FramePerSec.tick(FPS)
    
    