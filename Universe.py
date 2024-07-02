#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:49:55 2024

@author: zetadin
"""

import pygame

class Universe():
    def __init__(self, simsize: int = 128, parallel=False):
        if(simsize<=0):
            raise ValueError("simsize has to be a positive integer.")
        self.simsize = simsize
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
        
        self.drawables.empty()
        self.updatables.clear()
        self.collectables.clear()
        self.collidables.clear()
        self.destroy_these_structures=[]
        
    def destroyRequested(self):
        """
        Destroy entities after the update step.
        Needs to be after update to avoid iterating through a missing entity.
        """
        for e in self.destroy_these_structures:
            e.destroy()
        self.destroy_these_structures=[]
        
        
    def collisionDetect(self, dt):
        # check for structure-structure collisions
        for i in range(len(self.collidables)-1):
            si = self.collidables[i]
            for j in range(i+1, len(self.collidables)):
                sj = self.collidables[j]
                if(si.checkCollision(sj, dt)):
                    si.collidedWith(sj)
                    sj.collidedWith(si)
                    break
                    
        self.destroyRequested()
            
        
#    def collisionDetectWPlayer(self, player, dt):
#        for si in self.structures:
#            if(si.checkCollision(player, dt)):
#                si.collidedWPlayer()
            
        
            
universe = Universe(128, parallel=False)
SIM_SIZE = universe.simsize

# game object lists for this universe
drawables = universe.drawables
updatables = universe.updatables
collectables = universe.collectables
collidables = universe.collidables
