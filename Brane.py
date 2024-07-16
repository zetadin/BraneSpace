#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:37:21 2024

@author: zetadin
"""

import numpy as np
import numpy.typing as npt
import pygame
import GlobalRules
from utils.Geometry import expandPeriodicImages


VV = 32/1000.
LL = 16


class Brane(pygame.sprite.Sprite):
    def __init__(self, surf_scale: float, view: "View"):
        super().__init__()
        self.setView(view)
        
        self.surfScale = surf_scale
        self.calculateSimShape()
        
        self.I = None # intensity
        self.surf = None # temporary
        
        self.elapsed = 0.
        self.wavelets=[]
        self.drawGradients = False
        
        self.parentUniverse = None
        
        
    def setView(self, view: "View"):
        """
        Link Brane to a view so info about screen size is acessible.
        """
        self.view = view
        
        
    def calculateSimShape(self):
        """
        Calculate the dimentions of the simulation to fill the window
        and the coordinate grid that spans it.
        """
        screenShape = np.array(self.view.displaysurface.get_size())
        self.simShape = np.ceil(screenShape/self.surfScale).astype(int)
        
        # also compute the coordinate grid in world coords
        grid_x = np.arange(self.simShape[0])*self.surfScale
        grid_y = np.arange(self.simShape[1])*self.surfScale
               
        self.base_coords = np.zeros((self.simShape[0], self.simShape[1], 2))
        self.base_coords[:,:,0] = np.repeat(grid_x[:,np.newaxis],
                                       self.simShape[0], axis=1)
        self.base_coords[:,:,1] = np.repeat(grid_y[np.newaxis,:],
                                       self.simShape[1], axis=0)
        self.coords = self.base_coords
        
    def update(self, dt: float):
        """
        Calculate sum of all wavelet intensities in the simulated region.
        """
        # move coords so they are centered on screen
        center_in_coords = self.simShape*self.surfScale*0.5
        offset = self.view.center - center_in_coords
        self.coords = self.base_coords + offset
        
        # warp coords into primary box image
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            self.coords = np.fmod(self.coords, GlobalRules.curUniverseSize)
            self.coords[self.coords<0] += GlobalRules.curUniverseSize
        
        # update the intensity
        self.I = np.zeros(self.simShape)
        for wl in self.wavelets:
            wl.update(dt)
            self.I += wl.f(self.coords.reshape(-1,2)).reshape(self.simShape)


    def draw(self, view):
        """
        Draw to screen
        """
        if(view is not self.view): # view changed and Brane was not told!
            # set new view, recalculate grid, and update intensity
            self.setView(view)
            self.calculateSimShape()
            self.I = np.zeros(self.simShape)
            for wl in self.wavelets:
                self.I += wl.f(self.coords.reshape(-1,2)).reshape(self.simShape)
        
        if(self.I is None):
            # We may have started paused, so no updates have occured yet
            # Calculate intensity now.
            self.I = np.zeros(self.simShape)
            for wl in self.wavelets:
                self.I += wl.f(self.coords.reshape(-1,2)).reshape(self.simShape)
                
#        # debug surf size
#        self.I = np.zeros(self.simShape)
#        self.I[np.floor(self.simShape[0]*1/4).astype(int) : np.floor(self.simShape[0]*3/4).astype(int),
#               np.floor(self.simShape[1]*1/4).astype(int) : np.floor(self.simShape[1]*3/4).astype(int)] = 0.05
#               
#        self.I[0:4,:] = 1
#        self.I[-5:-1,:] = 1
#        self.I[:,0:4] = 1
#        self.I[:,-5:-1] = 1
        
            
        # re-paint the surface from simulation
        amp_arr = np.floor(np.clip(256*(self.I*4.0+1)/2, 0,255)).astype(np.uint8)
        amp_arr = np.repeat(amp_arr[:, :, np.newaxis], 3, axis=2)
        amp_surf = pygame.surfarray.make_surface(amp_arr)
        
        # gradients
        if(self.drawGradients):
            gcoords = self.coords.reshape((-1,2))
            grad_arr = self.computeForceAt(gcoords)
            grad_arr = grad_arr.reshape((self.simShape[0],self.simShape[1],2))
            grad_colors = np.zeros((self.simShape[0],self.simShape[1],3)).astype(np.uint8)
            # x -> red
            grad_colors[:,:,0] = np.floor(np.clip(256*(grad_arr[:,:,0]+1)/2, 0,255)).astype(np.uint8)
            # y -> green
            grad_colors[:,:,1] = np.floor(np.clip(256*(grad_arr[:,:,1]+1)/2, 0,255)).astype(np.uint8)
            # alpha
            grad_alpha = np.floor(np.clip(np.max(np.abs(grad_arr), axis=-1), 0.0, 0.1)*2550).astype(np.uint8)
        
            # new surface for gradient
            grad_surf = pygame.Surface((self.simShape[0],self.simShape[1]), pygame.SRCALPHA, 32)
            # Copy the rgb part of array to the new surface.
            pygame.pixelcopy.array_to_surface(grad_surf, grad_colors)
    
            # overwrite grad_surf's alpha
            gsa = np.array(grad_surf.get_view('A'), copy=False)
            gsa[:,:] = grad_alpha
            del gsa # to unlock grad_surf to allow blit 
            
            # draw onto intensity's surface
            amp_surf.blit(grad_surf, grad_surf.get_rect())

        # transform into screen coords
        self.surf = pygame.transform.smoothscale_by(
                        amp_surf, self.surfScale*self.view.zoom)
        
        # draw to screen
        self.view.drawSurfToView(self.surf, view.center)
        
        
    def computeForceAt(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Compute force from wavelets at given world coordinates.
        """
        # if PBC, wrap position into primary cell
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            x = np.fmod(x, GlobalRules.curUniverseSize)
            x[x<0] += GlobalRules.curUniverseSize
        
        # ask all wavelets for their force contributions
        F = np.zeros(x.shape)
        for wl in self.wavelets:
            F -= wl.gradf(x.reshape(-1,2)).reshape(x.shape)
        return(F)