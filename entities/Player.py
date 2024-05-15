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
from wavelets.Tractor import Tractor
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
        self.theta = -np.pi*0.5
        
        self.tractorElapsed = 0.0
        
        
    def update(self, dt: float):
        super().update(dt)
        
        # spin ship for demo of rotation
        self.theta -= dt*np.pi/4000. # 180 deg in 2 sec
        
        
        # every L/(2*v) seconds emit a tractor wavelet
        self.tractorElapsed += dt
        pulseTime = 8.0*0.5/3.2e-2
        if(self.tractorElapsed > pulseTime):
            self.tractorElapsed -= pulseTime
            
            # where the beam is heading
            direction = np.array([-np.sin(self.theta), -np.cos(self.theta)])
            # source of the wave in sim coords
            # a bit forward of player ship
            start = self.r/self.parentBrane.surfScale + 3*direction 
            wl = Tractor(source=start, direction=direction,
                         v = 3.2e-2,
                         L = 8.0,
                         A = 0.1,
                         Rmax = 128./self.parentBrane.surfScale, # in sim coords
                         debug=False)
            wl.alive = self.tractorElapsed
            wl.register(self.parentBrane)
        
        
            