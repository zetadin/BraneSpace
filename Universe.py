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
        
        self.game_over = False
        
        self.drawables = pygame.sprite.Group()
        self.updatables=[]
        self.collectables=[]
        self.structures=[]
        
        self.destroy_these_structures=[]
        
        # if we use multiple cores, create a shared memory
        # to hold entity positions and velocities
        # as they will be updated in the physics process
        if(self.parallel):
            pass
        
        
    def destroy_requested(self):
        """
        Destroy entities after the update step.
        Needs to be after update to avoid iterating through a missing entity.
        """
        for e in self.destroy_these_structures:
            e.destroy()
        self.destroy_these_structures=[]
        
        
    def collision_detect(self, dt):
        # check for structure-structure collisions
        for i in range(len(self.structures)-1):
            si = self.structures[i]
            for j in range(i+1, len(self.structures)):
                sj = self.structures[j]
                if(si.checkCollision(sj, dt)):
                    print(f"Structure collision: {i} & {j}")
                    si.collided_with(sj)
                    sj.collided_with(si)
                    break
                    
        self.destroy_requested()
            
        
    def collision_detect_w_player(self, player, dt):
        for si in self.structures:
            if(si.checkCollision(player, dt)):
                si.collided_w_player()
            
        
            
universe = Universe(128, parallel=False)
SIM_SIZE = universe.simsize

# game object lists for this universe
drawables = universe.drawables
updatables = universe.updatables
collectables = universe.collectables
structures = universe.structures
