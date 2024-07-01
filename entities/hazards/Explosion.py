#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 14:23:17 2024

@author: zetadin
"""

import numpy as np
import pygame
from pygame.locals import *
from entities.structures.Structure import Structure
from entities.resources.Resources import DarkMatter
from Universe import universe
from utils.AssetFactory import assetFactory


class Explosion(Structure):
    def __init__(self):
        super().__init__()
        
        # create/load image
        self.img = assetFactory.loadImg("entities/hazards/explosion.png", True)
        # needs to be a local copy to allow per-explosion alpha
        self.img = self.img.copy() 
        
        self.minSize = 32
        self.maxSize = self.minSize*2
        
        self.size = 32 # px
        self.collisionSize = 0.4*self.size
        
        self.maxLifeTime = 1000 # ms
        self.curLifeTime = 0   # ms
        
        # physics properties
        self.mass = 1.0e4
        self.dragCoef = 0.002
        
        self.rot_vel = np.random.uniform(-0.5, 0.5)*np.pi/1000 # +-90 deg/s
        self.theta = np.random.uniform(-1, 1)*np.pi
        
    def update(self, dt: float):
        super().update(dt)
        
        #rotation
        self.theta -= dt*self.rot_vel
        
        # lifetime
        self.curLifeTime += dt
        if(self.curLifeTime > self.maxLifeTime):
            self.destroy()
        else:
            # update size
            factor = self.curLifeTime/self.maxLifeTime
            self.size = self.minSize*(1-factor) + self.maxSize*factor
            self.collisionSize = 0.5*self.size
            
            # overwrite img's alpha
            img_a = np.array(self.img.get_view('A'), copy=False)
            img_a[img_a>0] = 180*(1.0 - factor)
            del img_a # to unlock img and allow blit


    def collidedWPlayer(self):
        """Handle collision with player.
        Player crashed."""
        universe.game_over = True