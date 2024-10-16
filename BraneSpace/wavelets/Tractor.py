#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 10:21:47 2024

@author: zetadin
"""

import numpy as np
import numpy.typing as npt
import pygame
import BraneSpace.core.GlobalRules as GlobalRules
from BraneSpace.utils.Geometry import expandPeriodicImages
from BraneSpace.wavelets.Wavelet import Wavelet


class Tractor(Wavelet, pygame.sprite.Sprite):
    def __init__(self, source: npt.ArrayLike,
                 direction: npt.ArrayLike,
                 v: float = 3.2e-2,
                 L: float = 16,
                 A: float = 0.1,
                 Rmax: float = 128.0,
                 theta0: float = np.pi/6.0,
                 debug=False):
        
        self.v = v
        self.L = L
        self.A = A
        self.Rmax = Rmax # Intencity 0 after this distance
        self.theta0 = theta0
        
        self.R = source
        self.dir = direction/np.linalg.norm(direction)
        
        # lifetime
        self.maxLifetime = (self.Rmax + self.L)/self.v
        self.lifetime = 0
        
        # registration
        self.parentBrane = None
        
        # debug
        self.debug = debug
        if(self.debug):
            pygame.sprite.Sprite.__init__(self) # manually init the Sprite
            
            self.size = 4
            self.img = pygame.Surface((self.size, self.size),
                                      flags=pygame.SRCALPHA) 
            pygame.draw.circle(
                    surface=self.img, color=(0, 0, 255, 255),
                    center=(self.size/2, self.size/2), radius=2
                    )
        
        
    def register(self, brane: "Brane"):
        """Add to the list of objects in the universe."""
        super().register(brane)
        
        if self.debug:
            self.parentBrane.parentUniverse.drawables.add(self)
            
        
    def update(self, dt: float):
        super().update(dt)
        
        # remove wavelet from drawables after its lifetime is over
        if self.debug:
            if(self.lifetime > self.maxLifetime):
                drawables.remove(self)
                
    def draw(self, view):
        """
        Draw to screen
        """
        # update position on screen
        rect = self.img.get_rect(
                center=view.transform(self.R*self.parentBrane.surfScale)
                )
        
        # draw to screen
        view.displaysurface.blit(self.img, rect)
        
        
    def f(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Wavelet intencity at points x.
        x : array of 2D points in shape (n,2).
        """
        rprime = x - self.R[np.newaxis,:]        
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            # if pbc, distance should be to nearest periodic image           
            ab = np.abs(rprime)
            # both conditions ccan't be true at once
            rprime[ab > np.abs(rprime + GlobalRules.curUniverseSize)] += GlobalRules.curUniverseSize
            rprime[ab > np.abs(x - self.R[np.newaxis,:] - GlobalRules.curUniverseSize)] -= GlobalRules.curUniverseSize
            
        rprimeLen = np.linalg.norm(rprime, axis=-1)
        
        # Wavelet window, triangular: ___/\___
        W = 1.0 - 2.0*np.abs(rprimeLen - self.v*self.lifetime)/self.L
        mask = W>0.
        W = W[mask]
        
        I = np.zeros((x.shape[0]))
        if(np.any(mask)):  # only do this if there is an active point
        
            # distance dependence from source
            Id = self.A*(np.sqrt(self.Rmax) - np.sqrt(rprimeLen[mask]))
            Id = np.where(rprimeLen[mask] < self.Rmax, Id,
                          np.zeros(Id.shape)  # 0 if beyond cutoff
                          )
            # angle dependence
            cosTheta = np.dot(rprime[mask], self.dir)/rprimeLen[mask]
            Ia = cosTheta - np.cos(self.theta0) # liniar in cos(theta)
            Ia = np.where(Ia>0, Ia, 0.0)
            
            # putting it together:
            I[mask] = W * Id * Ia
        
        return(I)
    
    def gradf(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Gradient of wavelet intencity at point x.
        """
        rprime = x - self.R[np.newaxis,:]        
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            # if pbc, distance should be to nearest periodic image           
            ab = np.abs(rprime)
            # both conditions ccan't be true at once
            rprime[ab > np.abs(rprime + GlobalRules.curUniverseSize)] += GlobalRules.curUniverseSize
            rprime[ab > np.abs(x - self.R[np.newaxis,:] - GlobalRules.curUniverseSize)] -= GlobalRules.curUniverseSize
            
        rprimeLen = np.linalg.norm(rprime, axis=-1)
                
        # Wavelet window, triangular: ___/\___
        W = 1.0 - 2.0*np.abs(rprimeLen - self.v*self.lifetime)/self.L
        mask = W>0.
        W = W[mask]
        
        G = np.zeros(x.shape)
        if(np.any(mask)):  # only do this if there is an active point
            
            # distance dependence from source
            Id = self.A*(np.sqrt(self.Rmax) - np.sqrt(rprimeLen[mask]))
            Id = np.where(rprimeLen[mask] < self.Rmax, Id,
                          np.zeros(Id.shape)  # 0 if beyond cutoff
                          )
            # angle dependence
            cosTheta = np.dot(rprime[mask], self.dir)/rprimeLen[mask]
            Ia = cosTheta - np.cos(self.theta0) # liniar in cos(theta)
            Ia = np.where(Ia>0, Ia, 0.0)
            
            
            # gradients of components
            gradrprime = rprime[mask]/rprimeLen[mask][:,np.newaxis]
            
            gradId = self.A*(np.sqrt(self.Rmax) + 0.5/np.sqrt(rprimeLen[mask]))
            gradId = gradId[:,np.newaxis] * gradrprime
            gradId = np.where(rprimeLen[mask][:,np.newaxis] < self.Rmax, gradId, 0.0)
            

            gradIa = self.dir[np.newaxis,:] - (cosTheta[:,np.newaxis]*gradrprime)/(rprimeLen[mask]*rprimeLen[mask])[:,np.newaxis]
            # apply the max for angular dependence too
            gradIa = np.where(cosTheta[:,np.newaxis] > np.cos(self.theta0),
                             gradIa, 0.0)

            
            relpos = rprimeLen[mask] - self.v*self.lifetime
            gradW = np.where(np.logical_and(relpos>0, relpos<0.5*self.L),
                             -2.0/self.L, 0.0) # 0 at peak of np.abs
            gradW = np.where(np.logical_and(relpos<0, relpos>-0.5*self.L),
                             +2.0/self.L, gradW)
            gradW = gradW[:,np.newaxis] * gradrprime
    
            # chain rule the contributions
            Ia = Ia[:,np.newaxis]
            Id = Id[:,np.newaxis]
            W = W[:,np.newaxis]

            G[mask] = (gradId*Ia + Id*gradIa)*W + Id*Ia*gradW

#        end_time = time.time()
#        print("pre:", pre_time-start_time, "\tloop:", post_time-pre_time, "\tI:", end_time-post_time)
        
        return(G)
    