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

from wavelets.Wavelet import Wavelet
from Universe import SIM_SIZE, updatables, drawables
from View import HEIGHT, WIDTH


VV = 32/1000.
LL = 16


class Brane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.I = np.zeros((SIM_SIZE, SIM_SIZE))
        self.I[16, 16] = 1.
        self.surf = pygame.Surface((2, 2)) # temporary
        self.surf.fill((128,128,128))
        
        self.surfSize = max(WIDTH, HEIGHT)
        self.surfScale = float(self.surfSize)/SIM_SIZE
        self.rect = pygame.Rect(0,0,self.surfSize,self.surfSize)
        
        pos = np.arange(SIM_SIZE)
        self.coords = np.zeros((SIM_SIZE, SIM_SIZE, 2))
        self.coords[:,:,0] = np.repeat(pos[:,np.newaxis], SIM_SIZE, axis=1)
        self.coords[:,:,1] = np.repeat(pos[np.newaxis,:], SIM_SIZE, axis=0)
        
        self.elapsed = 0.
        
        self.wavelets=[]
        
        # add initial wavelet
        wl = Wavelet(v = VV, L=LL, A=2.5, source=np.array([16.,16.]))
        wl.register(self)
        
    def register(self):
        # put into game object lists
        drawables.add(self)
        updatables.append(self)
        
        
    def update(self, dt: float):
        # update the intensity
        self.I = np.zeros((SIM_SIZE, SIM_SIZE))
        for wl in self.wavelets:
            wl.update(dt)
            self.I += wl.f(self.coords)
        
        # add a new wavelet every so often
        self.elapsed += dt
        if(self.elapsed > 2000):
            self.elapsed = 0.
#            R = np.random.random((2))*SIM_SIZE
#            wl = Wavelet(v = VV, L = LL, A=2.5, source=R)
#            wl.register(self)


    def draw(self, view):
        """
        Draw to screen
        """
        
        screen = view.displaysurface
        
        # re-paint the surface from simulation
        amp_arr = np.floor(np.clip(256*(self.I+1)/2, 0,255)).astype(np.uint8)
        amp_arr = np.repeat(amp_arr[:, :, np.newaxis], 3, axis=2)
        amp_surf = pygame.surfarray.make_surface(amp_arr)
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