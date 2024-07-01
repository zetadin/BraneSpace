#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:01:10 2024

@author: zetadin
"""

import numpy as np
from entities.Entity import SpriteEntity
from Universe import updatables, drawables, structures

class Structure(SpriteEntity):
    def updateBrane(self, dt: float):
        """
        Update brane's intensity with local effects
        """
        pass
    
    def register(self, brane: "Brane"):
        """Add to the list of objects in the universe."""
        super().register(brane)
        structures.append(self)
        
    def collided_with(self, other):
        """Handle collisions."""
        pass;
        
    def collided_w_player(self):
        """Handle collision with player."""
        pass;
    
    def destroy(self):
        if self in structures: structures.remove(self)
        if self in updatables: updatables.remove(self)
        if self in drawables: drawables.remove(self)
