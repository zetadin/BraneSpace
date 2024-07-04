#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:49:55 2024

@author: zetadin
"""

import pygame
import GlobalRules
from Brane import Brane


class Universe():
    def __init__(self, simSize: int = 128, parallel=False):
        if(simSize<=0):
            raise ValueError("simsize has to be a positive integer.")
        self.simSize = simSize
        self.parallel = parallel
        
        self.drawables = pygame.sprite.Group()
        self.updatables=[]
        self.collectables=[]
        self.collidables=[]
        
        self.reset()
        
        # if we use multiple cores, create a shared memory
        # to hold entity positions and velocities
        # as they will be updated in the physics process
        if(self.parallel):
            pass
        
    def reset(self):
        """
        Call when game (re)starts.
        """
        self.game_over = False
        self.paused = True
        
        self.drawables.empty()
        self.updatables.clear()
        self.collectables.clear()
        self.collidables.clear()
        self.destroy_these_collidables=[]
        
        if(GlobalRules.mode == GlobalRules.GameMode.ASTEROIDS):
            GlobalRules.pbc = GlobalRules.PBC.TOROIDAL
            GlobalRules.curUniverseSize = GlobalRules.WIDTH
        else:
            GlobalRules.pbc = GlobalRules.PBC.NONE
            GlobalRules.curUniverseSize = None
            
        # Create a new brane with no wavelets
        self.brane = Brane(self.simSize)
        # register brane here to avoid a circular import
        self.drawables.add(self.brane)
        self.updatables.append(self.brane)
        self.brane.parentUniverse = self
        
        
    def destroyRequested(self):
        """
        Destroy entities after the update step.
        Needs to be after update to avoid iterating through a missing entity.
        """
        for e in self.destroy_these_collidables:
            e.destroy()
        self.destroy_these_collidables=[]
        
        
    def collisionDetect(self, dt):
        # check for all collidable-collidable pairs
        for i in range(len(self.collidables)-1):
            si = self.collidables[i]
            if(si.alive): # don't check collidables that are already destoyed
                for j in range(i+1, len(self.collidables)):
                    sj = self.collidables[j]
                    if(sj.alive):
                        if(si.checkCollision(sj, dt)):
                            si.collidedWith(sj)
                            sj.collidedWith(si)
                            break
                    
        self.destroyRequested()
            
        
            
universe = Universe(128, parallel=False)
SIM_SIZE = universe.simSize

# game object lists for this universe
drawables = universe.drawables
updatables = universe.updatables
collectables = universe.collectables
collidables = universe.collidables
