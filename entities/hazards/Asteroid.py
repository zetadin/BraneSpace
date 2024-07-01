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
from entities.resources.Resources import DarkMatter
from Universe import universe
from utils.AssetFactory import assetFactory
from entities.hazards.Explosion import Explosion


class Asteroid(Structure):
    def __init__(self):
        super().__init__()
        
        # create/load image
        self.img = assetFactory.loadImg("entities/hazards/rock.png", True)
        self.size = 32 # px
        self.collisionSize = 0.75*self.size
        
        # physics properties
        self.mass = 1.0e4
        self.dragCoef = 0.002
        
        self.rot_vel = np.random.uniform(-0.5, 0.5)*np.pi/1000 # +-90 deg/s
        self.theta = np.random.uniform(-1, 1)*np.pi
        
    def update(self, dt: float):
        super().update(dt)
        
        #rotation
        self.theta -= dt*self.rot_vel

    def collidedWith(self, other):
        """Handle collisions.
        Asteroid gets destroyed and spawns some dark matter.
        """
        COM_v = (self.v*self.mass + other.v*other.mass)/(self.mass+other.mass)
        for i in range(np.random.randint(1,3)):
            loot = DarkMatter()
            loot.r = self.r
            loot.v = COM_v + (np.random.random(2) - 0.5)*0.1
            loot.register(self.parentBrane)
            
        expl = Explosion()
        expl.r = self.r
        expl.v = self.v
        expl.register(self.parentBrane)
            
        # request destruction, delayed until end of update
        universe.destroy_these_structures.append(self)
        
    def collidedWPlayer(self):
        """Handle collision with player.
        Player crashed."""
        universe.game_over = True