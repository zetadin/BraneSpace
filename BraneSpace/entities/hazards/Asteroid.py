#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:01:10 2024

@author: zetadin
"""

import numpy as np
from BraneSpace.entities.Collidable import Collidable
from BraneSpace.entities.resources.Resources import DarkMatter
from BraneSpace.utils.AssetFactory import assetFactory
from BraneSpace.entities.hazards.Explosion import Explosion


class Asteroid(Collidable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # create/load image
        self.img = assetFactory.loadImg("entities/hazards/rock.png", True)
        self.size = 32 # px
        self.collisionRadius = 0.45*self.size
        
        # physics properties
        self.mass = 1.0e4
        self.dragCoef = 0.002
        
        self.rot_vel = np.random.uniform(-0.5, 0.5)*np.pi/1000 # +-90 deg/s
        self.theta = np.random.uniform(-1, 1)*np.pi
        
        # growing
        self.grow = False
        self.maxGrowTime = 2000.
        self.curGrowTime = 0.
        

    def collidedWith(self, other):
        """Handle collisions.
        Asteroid gets destroyed and spawns some dark matter.
        """
        COM_v = (self.v*self.mass + other.v*other.mass)/(self.mass+other.mass)
        #for i in range(np.random.randint(1,3)):
        for i in range(1):
            loot = DarkMatter()
            loot.r = self.r
            loot.v = COM_v + (np.random.random(2) - 0.5)*0.1
            loot.register(self.parentBrane)
            
        expl = Explosion()
        expl.r = self.r
        expl.v = self.v
        expl.register(self.parentBrane)
            
        # request destruction, delayed until end of update
        self.alive = False # don't collision detect agains this anymore
        self.parentBrane.parentUniverse.destroy_these_collidables.append(self)

    def update(self, dt: float):
        super().update(dt)
        
        # lifetime
        if(self.grow):
            self.curGrowTime += dt
            if(self.curGrowTime > self.maxGrowTime):
                # stop growing
                self.grow = False
            else:
                # update size
                factor = self.curGrowTime/self.maxGrowTime
                self.size = 32*factor
                self.collisionRadius = 0.45*self.size
                