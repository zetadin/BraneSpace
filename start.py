import sys
import pygame
from pygame.locals import *

import numpy as np


from Brane import Brane
from View import View, HEIGHT, WIDTH, FPS
from entities.Entity import SpriteEntity
from entities.SimpleObjects import Ball
from entities.resources.Resources import DarkMatter
from entities.structures.Portal import Portal
from entities.hazards.Asteroid import Asteroid
from entities.Player import Player
from Universe import updatables, drawables, collectables, universe
from UI.TopBar import TopBar
import time


view = View()

# init UI
tb = TopBar(view)

        
# init objects in universe
cur_brane = Brane()
cur_brane.register()

for i in range(20):
    loot = DarkMatter()
    loot.r = np.random.random(2)*WIDTH
    loot.v = (np.random.random(2) - 0.5)*0.05
    loot.register(cur_brane)
    
for i in range(20):
    roid = Asteroid()
    roid.r = np.random.random(2)*WIDTH*0.8 + 0.1*WIDTH
    roid.v = (np.random.random(2) - 0.5)*0.01
    roid.register(cur_brane)
    

player = Player()
player.register(cur_brane)
tb.bindPlayer(player)

#portal = Portal()
#portal.r = np.array([WIDTH*0.7, WIDTH*0.7])
#portal.register(cur_brane)
#
#filler = SpriteEntity()
#filler.r = np.array([115.,215.])
#filler.register(cur_brane)

# initial guess at frame time
dt = 1000./FPS

updatesPerFrame = 1     # start with 1
maxUpdatesPerFrame = 1  # increase to this many if fast enough
update_dt = dt/updatesPerFrame


first_frame=True

# game loop
while True:
    
    # event processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            # rotation
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                player.rotationDirection = -1.0
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                player.rotationDirection = +1.0
            # thrust
            elif event.key in [pygame.K_UP, pygame.K_w]:
                player.fwd = True
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                player.bck = True
            # tractor
            elif event.key == pygame.K_SPACE:
                player.tractor = True
                
        if event.type == pygame.KEYUP:
            # rotation
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT,
                             pygame.K_a, pygame.K_d]:
                player.rotationDirection = 0.0
            # thrust
            elif event.key in [pygame.K_UP, pygame.K_w]:
                player.fwd = False
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                player.bck = False
            # tractor
            elif event.key == pygame.K_SPACE:
                player.tractor = False
                
            # quit
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                
            
            
            
            
    update_ms_left = min(dt, 1000./FPS)*0.8
    update_ms = 1000
    for u in range(updatesPerFrame):
        startTime = time.time()
        
        # update objects
        for entity in updatables:
            entity.update(update_dt)
            
        # structure-structure collisions
        if(first_frame):
            first_frame = False
        else:
            universe.update(update_dt)
            
        # attepmpt picking up collectables
        player.attemptPickUp(collectables, view, update_dt)
        
        update_ms = (time.time()-startTime)*1000.
        update_ms_left -= update_ms
        # remainingUpdates = updatesPerFrame - 1 - u
        if(update_ms_left < update_ms and u+1!=updatesPerFrame):
            # not enough time for another update,
            # and this is not the last scheduled one
            break
            
    
    
     
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
    
    # recalculate updatesPerFrame
    updatesPerFrame = min(int(min(dt, 1000./FPS)*0.8/update_ms), maxUpdatesPerFrame)
    updatesPerFrame = max(1, updatesPerFrame)
    update_dt = dt/updatesPerFrame
    
    