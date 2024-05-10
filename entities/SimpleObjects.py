#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:56:15 2024

@author: zetadin
"""

import pygame
from pygame.locals import *
from entities.Entity import SpriteEntity


class Ball(SpriteEntity):
    def __init__(self):
        super().__init__()
        
        # create/load image
        self.size = 10 # px
        self.img = pygame.Surface((self.size, self.size), flags=SRCALPHA) 
        pygame.draw.circle(
                surface=self.img, color=(255, 0, 0, 255),
                center=(self.size/2, self.size/2), radius=5
                )
        
        # physics properties
        self.mass = 1.0e2
        self.dragCoef = 0.1
        