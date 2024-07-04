import sys
import pygame
from pygame.locals import *

import numpy as np


#import GlobalRules
from Brane import Brane
from View import View
from GlobalRules import HEIGHT, WIDTH, FPS
from entities.Entity import SpriteEntity
from entities.SimpleObjects import Ball
from entities.resources.Resources import DarkMatter
from entities.structures.Portal import Portal
from entities.hazards.Asteroid import Asteroid
from entities.Player import Player
from Universe import updatables, drawables, collectables, universe
from UI.TopBar import TopBar
from utils.AssetFactory import assetFactory
import time


universe.reset()
view = View()
view.debug = True

# init UI
tb = TopBar(view)

# init game_over msg
game_over_font = pygame.font.SysFont('liberationserif', 64)
game_over_surf = game_over_font.render("Game Over", True, (219,188,86))

# init paused msg
pause_font = pygame.font.SysFont('liberationserif', 42)
pause_surf = pause_font.render("Press <RETURN> to Play",
                                   True, (219,188,86))

# load assets
assetFactory.preloadAll()

# init objects in universe
player = Player()
player.register(universe.brane)
tb.bindPlayer(player)

selfdot = lambda x : np.dot(x,x)
for i in range(0):
    loot = DarkMatter()
    loot.r = np.random.random(2)*WIDTH
    while(selfdot(loot.r-player.r) < player.size*player.size):
        loot.r = np.random.random(2)*WIDTH
    loot.v = (np.random.random(2) - 0.5)*0.05
    loot.register(universe.brane)
    
for i in range(20):
    roid = Asteroid()
    roid.r = np.random.random(2)*WIDTH*0.8 + 0.1*WIDTH
    while(selfdot(roid.r-player.r) < player.size*player.size):
        roid.r = np.random.random(2)*WIDTH
    roid.v = (np.random.random(2) - 0.5)*0.01
    roid.register(universe.brane)



#portal = Portal()
#portal.r = np.array([WIDTH*0.7, WIDTH*0.7])
#portal.register(universe.brane)


# initial guess at frame time
dt = 1000./FPS

updatesPerFrame = 1     # start with 1
maxUpdatesPerFrame = 1  # increase to this many if fast enough
update_dt = dt/updatesPerFrame




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
                
            # quit
            elif event.key == pygame.K_RETURN:
                universe.paused = not universe.paused
                
            
    # run the force calculation, position updates, and collision detection
    update_ms_left = min(dt, 1000./FPS)*0.8
    update_ms = 1000
    if(not universe.game_over and not universe.paused):
        for u in range(updatesPerFrame):
            startTime = time.time()
            
            # update objects
            for entity in updatables:
                entity.update(update_dt)
                
            # collisions between collidables (including player)
            universe.collisionDetect(update_dt)
                
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
    
    # draw Game Over
    if(universe.game_over):
        screenWidth, screenHeight = view.displaysurface.get_size()
        msgWidth, msgHeight = game_over_surf.get_size()
        view.displaysurface.blit(game_over_surf,(0.5*(screenWidth-msgWidth),
                                                 0.5*(screenHeight-msgHeight)))
    # draw pause
    if(universe.paused):
        screenWidth, screenHeight = view.displaysurface.get_size()
        msgWidth, msgHeight = pause_surf.get_size()
        view.displaysurface.blit(pause_surf,(0.5*(screenWidth-msgWidth),
                                             0.5*(screenHeight-msgHeight)))
    
    
 
    # push to frame buffer
    pygame.display.update()
    
    # wait for next frame
    dt = view.FramePerSec.tick(FPS)
    
    # recalculate updatesPerFrame
    updatesPerFrame = min(int(min(dt, 1000./FPS)*0.8/update_ms), maxUpdatesPerFrame)
    updatesPerFrame = max(1, updatesPerFrame)
    update_dt = dt/updatesPerFrame
    
    