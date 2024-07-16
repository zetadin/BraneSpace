#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:41:03 2024

@author: zetadin
"""

import numpy as np
import numpy.typing as npt
import BraneSpace.core.GlobalRules as GlobalRules
from BraneSpace.utils.Geometry import expandPeriodicImages

class Wavelet:
    """
    Sinusoidal wavelet that terminates after one wave length.
    """
    def __init__(self,v: float, L: float, A: float, source: npt.ArrayLike,
                 maxLifetime: float=2.0):
        self.v = v
        self.L = L
        self.A = A
        self.R = source
        
        self.k = 2*np.pi/self.L
        self.w = self.v*self.k
        
        # lifetime
        self.maxLifetime = maxLifetime
        self.lifetime = 0
        self.parentBrane = None
        
    def register(self, parentBrane: "Brane"):
        # if already registered with a brane, move wavelet to new one
        if(self.parentBrane):
            self.parentBrane.wavelets.remove(self)
        parentBrane.wavelets.append(self)
        self.parentBrane = parentBrane
        
    def update(self, dt: float):
        self.lifetime += dt
        
        # remove wavelet after lifetime is over
        if(self.lifetime > self.maxLifetime):
            self.parentBrane.wavelets.remove(self)
            self.parentBrane = None
        
    def f(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Wavelet intencity at points x.
        """        
        rprime = x - self.R       
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            # if pbc, distance should be to nearest periodic image           
            ab = np.abs(rprime)
            # both conditions ccan't be true at once
            rprime[ab > np.abs(rprime + GlobalRules.curUniverseSize)] += GlobalRules.curUniverseSize
            rprime[ab > np.abs(x - self.R - GlobalRules.curUniverseSize)] -= GlobalRules.curUniverseSize
            
        distMat = np.sqrt(np.sum(rprime*rprime, axis=-1))
        
        mask = np.logical_and(
                distMat <= self.v*self.lifetime,
                distMat >= max(0, self.v*self.lifetime - self.L)
                )
        I = np.zeros((x.shape[0], x.shape[1]))
        I[mask] = self.A*np.sin(self.k*distMat[mask] - self.w*self.lifetime)
        I[mask] /= self.v*self.lifetime # Conserve intensity with time
        return(I)
        
        
    def gradf(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Gradient of wavelet intencity at point x.
        """
        rprime = x - self.R       
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            # if pbc, distance should be to nearest periodic image           
            ab = np.abs(rprime)
            # both conditions ccan't be true at once
            rprime[ab > np.abs(rprime + GlobalRules.curUniverseSize)] += GlobalRules.curUniverseSize
            rprime[ab > np.abs(x - self.R - GlobalRules.curUniverseSize)] -= GlobalRules.curUniverseSize
            
        distMat = np.sqrt(np.sum(rprime*rprime, axis=-1))
        mask = np.logical_and(
                distMat <= self.v*self.lifetime,
                distMat >= max(0, self.v*self.lifetime - self.L)
                )

        G = np.zeros(x.shape)
        if(np.any(mask)):  # only do this if there is an active point
            G[mask] = (self.A*np.cos(self.k*distMat[mask] - self.w*self.lifetime))[:,np.newaxis]
            G[mask]*= rprime[mask,:] * self.k/(2*distMat[mask])[:,np.newaxis]
            G[mask]/= self.v*self.lifetime # Conserve intensity with time
        
        return(G)
