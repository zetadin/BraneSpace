#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:07:40 2024

@author: zetadin
"""

import numpy as np
import pygame
from pygame.locals import *
from entities.Entity import SpriteEntity
from View import HEIGHT, WIDTH


class Player(SpriteEntity):
    def __init__(self):
        super().__init__()
        self.img = pygame.image.load("assets/entities/player/rocket.png").convert_alpha()
        self.size = 64 # px
        
        # physics properties
        self.mass = 5.0e3
        self.dragCoef = 0.2
        # coordinates in world space
        self.r = np.array([WIDTH/3, WIDTH/3])
        
        
    def update(self, dt: float):
        super.update(dt)
        
        # spin ship for demo of rotation
        self.theta -= 0.01*dt*np.pi
        