#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:01:10 2024

@author: zetadin
"""

import numpy as np
import pygame
from pygame.locals import *
from entities.Collidable import Collidable
from utils.AssetFactory import assetFactory

class Portal(Collidable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # create/load image
        self.img = assetFactory.loadImg("entities/structures/portal.png", True)
        self.size = 128 # px
        self.collisionRadius = 0.5*self.size
        
        # physics properties
        self.mass = 1.0e9
        self.dragCoef = 20.
        
        # rotational velocity
        self.rot_vel = -np.pi/1000.

