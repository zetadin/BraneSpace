#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:01:10 2024

@author: zetadin
"""

import numpy as np
import pygame
from pygame.locals import *
from entities.Entity import SpriteEntity

class Portal(SpriteEntity):
    def __init__(self):
        super().__init__()
        
        # create/load image
        self.img = pygame.image.load("assets/entities/structures/portal.png").convert_alpha()
        self.size = 128 # px
        
        # physics properties
        self.mass = 1.0e9
        self.dragCoef = 20.

        
    def update(self, dt: float):
        super().update(dt)
        
        #rotation
        self.theta += dt*np.pi/1000. # 180 deg/s
        
    def updateBrane(self, dt: float):
        """
        Update brane's intensity with local effects
        """
        pass
