#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:01:10 2024

@author: zetadin
"""

import numpy as np
from entities.Entity import SpriteEntity
from Universe import updatables, drawables, collidables

class Collidable(SpriteEntity):
    
    def register(self, brane: "Brane"):
        """Add to the list of objects in the universe."""
        super().register(brane)
        collidables.append(self)
        
    def collidedWith(self, other):
        """Handle collisions."""
        pass;
        
    def destroy(self):
        """
        Every collidable should request it's own eventual
        destruction by this function.
        """
        if self in collidables: collidables.remove(self)
        if self in updatables: updatables.remove(self)
        if self in drawables: drawables.remove(self)
