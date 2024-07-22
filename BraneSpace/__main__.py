# Compilation options
#
# nuitka-project: --follow-imports
# nuitka-project: --standalone
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/assets=BraneSpace/assets
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/docs=docs
# nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/../rocket.ico
# nuitka-project: --product-name=BraneSpace
# nuitka-project: --product-version=0.0.1
# nuitka-project: --copyright="(c) 2024 Yuriy Khalak"


import sys
import pygame
from pygame.locals import *

import numpy as np


import BraneSpace.core.GlobalRules as GlobalRules
from BraneSpace.core.GlobalRules import HEIGHT, WIDTH, FPS
from BraneSpace.UI.View import View
from BraneSpace.entities.Entity import SpriteEntity
from BraneSpace.entities.SimpleObjects import Ball
from BraneSpace.entities.resources.Resources import DarkMatter
from BraneSpace.entities.structures.Portal import Portal
from BraneSpace.entities.hazards.Asteroid import Asteroid
from BraneSpace.entities.Player import Player
from BraneSpace.core.Universe import Universe
from BraneSpace.UI.TopBar import TopBar
from BraneSpace.utils.AssetFactory import assetFactory
import time

# helper function for computing distance squared
selfdot = lambda x : np.dot(x,x)


def reset(_uni, _tb, _view):
    """
    Resets the game state to starting conditions.
    Returns a new player instance.
    """
    # purge old entities
    _uni.reset()
    
    # create and resister a new Player
    player = Player(r = np.zeros(2), v = np.zeros(2))
    player.register(_uni.brane)
    _tb.bindPlayer(player)
    _view.setFocus(player)
    
    # create some starting objects
    # resources:
    for i in range(3):
        loot = DarkMatter()
        loot.r = np.random.random(2)*WIDTH
        while(selfdot(loot.r-player.r) < player.size*player.size):
            loot.r = np.random.random(2)*WIDTH
        loot.v = (np.random.random(2) - 0.5)*0.05
        loot.register(universe.brane)
        
    # asteroids:
    for i in range(10):
        roid = Asteroid()
        roid.r = np.random.random(2)*WIDTH
        while(selfdot(roid.r-player.r) < player.size*player.size*2):
            roid.r = np.random.random(2)*WIDTH
        roid.v = (np.random.random(2) - 0.5)*0.03
        roid.register(universe.brane)
        
    # staructures:
    #portal = Portal()
    #portal.r = np.array([WIDTH*0.7, WIDTH*0.7])
    #portal.register(universe.brane)
    
    return(player)


# create a viewport
view = View()
view.debug = False

# create a universe. It will in turn create a brane.
universe = Universe(view, parallel=False, braneSurfScale=4.0)

# init UI
tb = TopBar(view)

# init game_over msg
game_over_font = pygame.font.SysFont('liberationserif', 64)
game_over_surf = game_over_font.render("Game Over", True, (219,188,86))

# init paused msg
pause_font = pygame.font.SysFont('liberationserif', 42)
pause_surf = pause_font.render("Press <RETURN> to Play",
                                   True, (219,188,86))
help_font = pygame.font.SysFont('liberationserif', 22)
help_text ="""Don't touch asteroids.
Make them collide and collect dropped resources.

<WASD> or arrow keys to move
<SPACE> for repulsor beam
<SHIFT> + <SPACE> for tractor beam
<ESC> to quit"""


# load assets
assetFactory.preloadAll()

# init game state
player = reset(universe, tb, view);


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
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                player.bck = True
            # tractor/repulsor
            elif event.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                player.tractor = True
            elif event.key == pygame.K_SPACE:
                player.wavegen = True
                
        elif event.type == pygame.KEYUP:
            # rotation
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT,
                             pygame.K_a, pygame.K_d]:
                player.rotationDirection = 0.0
            # thrust
            elif event.key in [pygame.K_UP, pygame.K_w]:
                player.fwd = False
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                player.bck = False
            # tractor/repulsor
            elif event.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                player.tractor = False
            elif event.key == pygame.K_SPACE:
                player.wavegen = False
                
            # quit
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                
            # pause/resume
            elif event.key == pygame.K_RETURN:
                universe.paused = not universe.paused
                # resets if Game Over
                if(universe.game_over):
                    universe.reset()
                    print(player)
                
                
        elif event.type == pygame.VIDEORESIZE:
            # window changed size
            view.resize(event.w,event.h)
            tb.calcSizes(view)
                
            
    # run the force calculation, position updates, and collision detection
    update_ms_left = min(dt, 1000./FPS)*0.8
    update_ms = 1000
    if(not universe.game_over and not universe.paused):
        for u in range(updatesPerFrame):
            startTime = time.time()
            
            # update objects
            for entity in universe.updatables:
                entity.update(update_dt)
                
            # collisions between collidables (including player)
            universe.collisionDetect(update_dt)
                
            # attepmpt picking up collectables
            player.attemptPickUp(universe.collectables, view, update_dt)
            
            update_ms = (time.time()-startTime)*1000.
            update_ms_left -= update_ms
            # remainingUpdates = updatesPerFrame - 1 - u
            if(update_ms_left < update_ms and u+1!=updatesPerFrame):
                # not enough time for another update,
                # and this is not the last scheduled one
                break
    
    # update view after focus position has been updated
    view.update(dt)
    
    # show bounding primitives if game over
    if(universe.game_over):
        view.debug = True
    
    # do we need more hazards?
    desired_hazards = 15 + np.floor(1.5*np.sqrt(player.score))
    cur_hazards = [isinstance(c, Asteroid) for c in universe.collidables]
    cur_hazards = np.count_nonzero(cur_hazards)
    if(desired_hazards>cur_hazards):
        cus = GlobalRules.curUniverseSize
        min_dist_sq = (0.4*cus)**2
        
        # spawn more hazards if too few
        while desired_hazards>cur_hazards:
            roid = Asteroid()
            roid.grow = True
            roid.size = 0.
            roid.collisionRadius=0.
            if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
                roid.r = np.random.random(2)*cus
                # PBC wrap the difference
                dif = roid.r-player.r
                ab = np.abs(dif)
                dif[ab > np.abs(dif + cus)] += cus
                dif[ab > np.abs(roid.r-player.r - cus)] -= cus
                while(selfdot(dif) < min_dist_sq):
                    roid.r = np.random.random(2)*cus
                    dif = roid.r-player.r
                    ab = np.abs(dif)
                    dif[ab > np.abs(dif + cus)] += cus
                    dif[ab > np.abs(roid.r-player.r - cus)] -= cus
            else:
                raise(Exception("Asteroid spawning without PBC is unimplemented."))
                roid.r = np.random.random(2)*WIDTH
                while(selfdot(roid.r-player.r) < min_dist_sq):
                    roid.r = np.random.random(2)*WIDTH
            roid.v = (np.random.random(2) - 0.5)*0.06
            roid.register(universe.brane)
            cur_hazards += 1
     
    # wipe screen 
    view.displaysurface.fill((0,0,0))
 
    # draw everything
    for entity in universe.drawables:
        entity.draw(view)
        
        
    # draw the UI
    tb.draw(view)
    
    # draw Game Over
    if(universe.game_over):
        screenWidth, screenHeight = view.displaysurface.get_size()
        msgWidth, msgHeight = game_over_surf.get_size()
        view.displaysurface.blit(game_over_surf,(0.5*(screenWidth-msgWidth),
                                                 0.25*(screenHeight-msgHeight)))
    # draw pause
    if(universe.paused):
        screenWidth, screenHeight = view.displaysurface.get_size()
        msgWidth, msgHeight = pause_surf.get_size()
        view.displaysurface.blit(pause_surf,(0.5*(screenWidth-msgWidth),
                                             0.5*(screenHeight-msgHeight)))
        
        # show help on pause
        help_y_start = 0.6*screenHeight
        ls = help_font.get_linesize()
        for i,l in enumerate(help_text.splitlines()):
            help_line_surf = help_font.render(l, True, (219,188,86))
            msgWidth, msgHeight = help_line_surf.get_size()
            view.displaysurface.blit(help_line_surf,
                                     (0.5*(screenWidth-msgWidth),
                                      help_y_start + i*ls) )
    
    
 
    # push to frame buffer
    pygame.display.update()
    
    # wait for next frame
    dt = view.FramePerSec.tick(FPS)
    
    # recalculate updatesPerFrame
    updatesPerFrame = min(int(min(dt, 1000./FPS)*0.8/update_ms), maxUpdatesPerFrame)
    updatesPerFrame = max(1, updatesPerFrame)
    update_dt = dt/updatesPerFrame
    
    