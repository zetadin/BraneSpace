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
from utils.AssetFactory import assetFactory

class Portal(Structure):
    def __init__(self):
        super().__init__()
        
        # create/load image
        
        self.img = assetFactory.load_img("entities/structures/portal.png", True)
        self.size = 128 # px
        
        # physics properties
        self.mass = 1.0e9
        self.dragCoef = 20.

        
    def update(self, dt: float):
        super().update(dt)
        
        #rotation
        self.theta -= dt*np.pi/1000. # 180 deg/s
