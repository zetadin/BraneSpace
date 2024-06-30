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
        self.structures=[]
        
        # if we use multiple cores, create a shared memory
        # to hold entity positions and velocities
        # as they will be updated in the physics process
        if(self.parallel):
            pass
            
universe = Universe(128, parallel=False)
SIM_SIZE = universe.simsize

# game object lists for this universe
drawables = universe.drawables
updatables = universe.updatables
collectables = universe.collectables
structures = universe.structures