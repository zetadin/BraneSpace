#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:37:21 2024

@author: zetadin
"""

import numpy as np
import numpy.typing as npt
import pygame
from pygame.locals import *

from View import HEIGHT, WIDTH


VV = 32/1000.
LL = 16


class Brane(pygame.sprite.Sprite):
    def __init__(self, simSize: int):
        super().__init__()
        self.simSize = simSize
        self.I = np.zeros((self.simSize, self.simSize)) # intensity
        self.surf = pygame.Surface((2, 2)) # temporary
        self.surf.fill((128,128,128))
        
        self.surfSize = max(WIDTH, HEIGHT)
        self.surfScale = float(self.surfSize)/self.simSize
        self.rect = pygame.Rect(0,0,self.surfSize,self.surfSize)
        
        pos = np.arange(self.simSize)
        self.coords = np.zeros((self.simSize, self.simSize, 2))
        self.coords[:,:,0] = np.repeat(pos[:,np.newaxis], self.simSize, axis=1)
        self.coords[:,:,1] = np.repeat(pos[np.newaxis,:], self.simSize, axis=0)
        
        self.elapsed = 0.
        self.wavelets=[]
        self.drawGradients = False
        
        self.parentUniverse = None
        
        
    def update(self, dt: float):
        # update the intensity
        self.I = np.zeros((self.simSize, self.simSize))
        for wl in self.wavelets:
            wl.update(dt)
            self.I += wl.f(self.coords)


    def draw(self, view):
        """
        Draw to screen
        """
        
        screen = view.displaysurface
        
        # re-paint the surface from simulation
        amp_arr = np.floor(np.clip(256*(self.I*4.0+1)/2, 0,255)).astype(np.uint8)
        amp_arr = np.repeat(amp_arr[:, :, np.newaxis], 3, axis=2)
        amp_surf = pygame.surfarray.make_surface(amp_arr)
        
        # gradients
        if(self.drawGradients):
            gcoords = self.coords.reshape((-1,2))
            grad_arr = self.computeForceAt(gcoords*self.surfScale)
            grad_arr = grad_arr.reshape((self.simSize,self.simSize,2))
            grad_colors = np.zeros((self.simSize,self.simSize,3)).astype(np.uint8)
            # x -> red
            grad_colors[:,:,0] = np.floor(np.clip(256*(grad_arr[:,:,0]+1)/2, 0,255)).astype(np.uint8)
            # y -> green
            grad_colors[:,:,1] = np.floor(np.clip(256*(grad_arr[:,:,1]+1)/2, 0,255)).astype(np.uint8)
            # alpha
            grad_alpha = np.floor(np.clip(np.max(np.abs(grad_arr), axis=-1), 0.0, 0.1)*2550).astype(np.uint8)
        
            # new surface for gradient
            grad_surf = pygame.Surface((self.simSize,self.simSize), pygame.SRCALPHA, 32)
            # Copy the rgb part of array to the new surface.
            pygame.pixelcopy.array_to_surface(grad_surf, grad_colors)
    
            # overwrite grad_surf's alpha
            gsa = np.array(grad_surf.get_view('A'), copy=False)
            gsa[:,:] = grad_alpha
            del gsa # to unlock grad_surf to allow blit 
            
            # draw onto intensity's surface
            amp_surf.blit(grad_surf, grad_surf.get_rect())

        # transform into screen coords
        self.surf = pygame.transform.smoothscale(
                        amp_surf, (screen.get_width(), screen.get_height())
                        )
        
        # draw to screen
        screen.blit(self.surf, self.rect)
        
        
    def computeForceAt(self, x: npt.ArrayLike) -> npt.ArrayLike:
        # transform x into the simulation coordinates
        x = x/self.surfScale
        
        # ask all wavelets for their force contributions
        F = np.zeros(x.shape)
        for wl in self.wavelets:
            F -= wl.gradf(x)
            
        # move force back into screen coordinate space
        F *= self.surfScale
        return(F)