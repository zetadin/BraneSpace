#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:09:34 2024

@author: zetadin
"""

import numpy as np
import numpy.typing as npt
import pygame
from pygame.locals import *



HEIGHT = 600
WIDTH = 600
FPS = 60

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
        
        self.zoom = 1.
        self.center = self.screen_box*0.5 # in world coords
        
    def isOnScreen(self, ent: "Entity") -> bool:
        """
        Check if entity is in screen area and should be drawn.
        """
        dif = np.abs(self.center - ent.r)
        cond = dif < (0.5*self.screen_box + ent.size*np.sqrt(2))/self.zoom
        return(np.all(cond))
        
    def transform(self, r: npt) -> npt:
        """
        Transform coordinates from world to screen space.
        """
        return (r - self.center + 0.5*self.screen_box)/self.zoom
    