#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:09:34 2024

@author: zetadin
"""

import numpy as np
import numpy.typing as npt
import pygame
import GlobalRules
from utils.Geometry import expandPeriodicImages
from pygame.locals import *
from GlobalRules import HEIGHT, WIDTH

# cached value for optimization
SQRT2 = np.sqrt(2)

class View():
    def __init__(self):
        pygame.init()

        # start timer
        self.FramePerSec = pygame.time.Clock()
        
        # add a window
        self.screen_box = np.array([WIDTH, HEIGHT])
        self.displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("BraneSpace")
        
        # fonts
        pygame.font.init()
        self.serif_font = pygame.font.SysFont('liberationserif', 18)
        self.serif_font_px_size = 24 # size in pixels
        
        self.zoom = 1.
        self.center = self.screen_box*0.5 # in world coords
        
        self.debug = False
        
    def isOnScreen(self, ent: "Entity") -> bool:
        """
        Check if entity is in screen area and should be drawn.
        """
        
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            # if pbc, check if nearest image of ent is on screen
            pos = expandPeriodicImages(ent.r, GlobalRules.curUniverseSize)
        else:
            pos = ent.r[np.newaxis,:]

        dif = np.abs(self.center - pos)
        dif_sq = np.einsum("ij,ij->i", dif,dif) # dot only in last axis
        nearest = np.argmin(dif_sq) # index of nearest image
        cond = dif[nearest] < (0.5*self.screen_box + ent.size*SQRT2)/self.zoom
        return(np.all(cond))
        
    def periodicImagesOnScreen(self, ent: "Entity") -> (npt, npt):
        """
        Which periodic images are on screen?
        Returns theiir visibility along with in-universe image coordinates.
        """
        pos = expandPeriodicImages(ent.r, GlobalRules.curUniverseSize)
        dif = np.abs(self.center - pos)
        cond = dif < ((0.5*self.screen_box + ent.size*SQRT2)/self.zoom)[np.newaxis,:]
        return(np.all(cond, axis=-1), pos)
        
        
    def transform(self, r: npt) -> npt:
        """
        Transform coordinates from world to screen space.
        """
        return (r - self.center + 0.5*self.screen_box)/self.zoom
    