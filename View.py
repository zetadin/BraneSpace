#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:09:34 2024

@author: zetadin
"""

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
        self.displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("BraneSpace")
        
        # fonts
        pygame.font.init()
        self.serif_font = pygame.font.SysFont('liberationserif', 18)
    