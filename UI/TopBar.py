#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 12:59:10 2024

@author: zetadin
"""

import pygame
from pygame.locals import *
import numpy as np
from View import View


class TopBar(pygame.sprite.Sprite):
    def __init__(self, view: View):
        self.bkgImg = pygame.image.load("assets/UI/RustedMetal.png").convert()
        self.border = pygame.image.load("assets/UI/Toolbar_edge_128.png").convert()
        
        self.player = None
        
        self.calcSizes(view);
        
        
    def calcSizes(self, view: View):
        screen = view.displaysurface
        screenWidth, screenHeight = screen.get_size()
        self.width = screenWidth
        self.height = max(35, 0.05*screenHeight)
        
        # reblit the background
        self.barBackground = pygame.Surface((self.width,self.height))
        imgW, imgH = self.bkgImg.get_size()
        nX = int(np.ceil(self.width/imgW))
        nY = int(np.ceil(self.height/imgH))
        for x in range(nX):
            for y in range(nY):
                self.barBackground.blit(self.bkgImg, (x*imgW, y*imgH))
                
        # reblit the border
        imgW, imgH = self.border.get_size()
        nX = int(np.ceil(self.width/imgW))
        for x in range(nX):
            self.barBackground.blit(self.border, (x*imgW, self.height-imgH))
            
            
        # cells
        self.cellHeight = self.height - 8 # 4 px padding top & bottom
        self.cellBorder = 0 # px border width; 0-> fill
        self.cellRadius = 0 # px border radius
        
        # FPS
        self.fpsPos = 4
        self.fpsCell = pygame.Surface((int(8*view.serif_font_px_size*0.5),
                                       self.cellHeight), flags=SRCALPHA)
        pygame.draw.rect(
                surface=self.fpsCell, color=(30, 30, 60, 255),
                rect=self.fpsCell.get_rect(),
                width=self.cellBorder,
                border_radius = self.cellRadius)
        
        # Resources gathered (Score)
        self.scoreCell = pygame.Surface((int(8*view.serif_font_px_size*0.5),
                                       self.cellHeight), flags=SRCALPHA)
        self.scorePos = self.width - self.scoreCell.get_width() - 4
        pygame.draw.rect(
                surface=self.scoreCell, color=(30, 30, 60, 255),
                rect=self.scoreCell.get_rect(),
                width=self.cellBorder,
                border_radius = self.cellRadius)
        
    def bindPlayer(self, player: "Player"):
        self.player = player      
        
    
    def draw(self, view: View):
        """
        Draw to screen
        """
        
        # Background
        view.displaysurface.blit(self.barBackground, (0, 0))
        
        # show FPS
        text = view.serif_font.render(
            f"FPS: {view.FramePerSec.get_fps():.0f}",
            False, (200,200,200)
            )
        imgW, imgH = text.get_size()
        temp = self.fpsCell.copy()
        temp.blit(text, (4, int((self.cellHeight-imgH)*0.5)))
        view.displaysurface.blit(temp, (self.fpsPos, 4))
        
        # show score
        if(not self.player):
            score = 0
        else:
            score = self.player.score
        text = view.serif_font.render(
                f"{score:10d}",
                False, (200,200,200)
            )
        imgW, imgH = text.get_size()
        temp = self.scoreCell.copy()
        temp.blit(text, (int(self.scoreCell.get_width()-imgW-4),
                         int((self.cellHeight-imgH)*0.5))
                 )
        view.displaysurface.blit(temp, (self.scorePos, 4))
        
        
        
        