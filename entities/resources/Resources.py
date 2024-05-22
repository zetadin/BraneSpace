#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:02:29 2024

@author: zetadin
"""

import numpy as np
import numpy.typing as npt
import pygame
from entities.Entity import SpriteEntity
from Universe import updatables, drawables, collectables


class Collectable(SpriteEntity):
    """
    A SpriteEntity that can be picked up.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # forwards all unused arguments
        
    def register(self, brane: "Brane"):
        """Add to the list of objects in the universe."""
        super().register(brane)
        collectables.append(self)
        
    def addToPlayer(self, player: "Player"):
        """
        Should be overwritten by children.
        Set which Player property to increment.
        """
        pass
        
    def attemptPickUp(self, player: "Player", view: "View", dt: float):
        # culling, can't pick up things far away anyway
        sucess = False
        if(view.isOnScreen(self)):
            
            # line segment to circle collision
            # stationary circle by changing velocity of Collectable
            vdt = (self.v - player.collector_v) * dt # start to end
            x   = self.r - vdt                   # start pos
            cx  = player.collector_r - x         # start to center
            ce  = player.collector_r - self.r    # end to center
            
            if(np.dot(cx,cx)<=player.collect_radius_sq):
                sucess = True
            elif(np.dot(ce,ce)<=player.collect_radius_sq):
                sucess = True
            else:
                u = np.dot(cx, vdt)/np.dot(vdt,vdt)
                if(u>=0.0 and u<=1.0):
                    sucess = True
        
            if(sucess):
                # give to the player
                self.addToPlayer(player)
                
                # remove instance from object lists
                collectables.remove(self)
                updatables.remove(self)
                drawables.remove(self)
                # this instance can now be garbage collected


class DarkMatter(Collectable):
    def __init__(self):
        super().__init__()
        
        # create/load image
        self.img = pygame.image.load("assets/entities/resources/dark_matter.png").convert_alpha()
        self.size = 16 # px
        
        # physics properties
        self.mass = 5.0e1
        self.dragCoef = 0.05

        
    def addToPlayer(self, player: "Player"):
        """
        Set which Player property to increment.
        """
        # for now just put into the score
        player.score += 1
