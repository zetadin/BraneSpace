#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:02:29 2024

@author: zetadin
"""

import pygame
from entities.Entity import SpriteEntity

class DarkMatter(SpriteEntity):
    def __init__(self):
        super().__init__()
        
        # create/load image
        self.img = pygame.image.load("assets/entities/resources/dark_matter.png").convert_alpha()
        self.size = 16 # px
        
        # physics properties
        self.mass = 5.0e1
        self.dragCoef = 0.05

        
    def update(self, dt: float):
        super().update(dt)
        
        # does not rotate
