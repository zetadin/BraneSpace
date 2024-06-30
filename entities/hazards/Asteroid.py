#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:01:10 2024

@author: zetadin
"""

import numpy as np
import pygame
from pygame.locals import *
from entities.structures.Structure import Structure
from Universe import updatables, drawables, structures

class Asteroid(Structure):
    def __init__(self):
        super().__init__()
        
        # create/load image
        self.img = pygame.image.load("assets/entities/hazards/rock.png").convert_alpha()
        self.size = 32 # px
        
        # physics properties
        self.mass = 1.0e4
        self.dragCoef = 0.002
        
        self.rot_vel = np.random.uniform(-0.5, 0.5)*np.pi/1000 # +-90 deg/s

        
    def update(self, dt: float):
        super().update(dt)
        
        #rotation
        self.theta -= dt*self.rot_vel
        
    def register(self, brane: "Brane"):
        """Add to the list of objects in the universe."""
        super().register(brane)
        structures.append(self)
