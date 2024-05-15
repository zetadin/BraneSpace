#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 10:21:47 2024

@author: zetadin
"""

from wavelets.Wavelet import Wavelet
import numpy as np
import numpy.typing as npt


class Tractor(Wavelet):
    def __init__(self, source: npt.ArrayLike,
                 direction: npt.ArrayLike,
                 v: float = 3.2e-2,
                 L: float = 16,
                 A: float = 1.0,
                 Rmax: float = 128.0,
                 theta0: float = np.pi/6.0):
        self.v = v
        self.L = L
        self.A = A
        self.Rmax = Rmax # Intencity 0 after this distance
        self.theta0 = theta0
        
        self.R = source
        self.dir = direction/np.linalg.norm(direction)
        
        self.k = 2*np.pi/self.L
        self.w = self.v*self.k
        
        # lifetime
        self.maxLifetime = (self.Rmax + self.L)/self.v
        self.lifetime = 0
        self.parentBrane = None
        
    def f(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Wavelet intencity at points x.
        """
        rprime = x - self.R[np.newaxis,np.newaxis,:]
        rprimeLen = np.linalg.norm(rprime, axis=-1)
        
#        print(self.R)
#        print(rprimeLen.shape, np.min(rprimeLen), np.max(rprimeLen))
        
        
        # Wavelet window, triangular: ___/\___
        W = 1.0 - 2.0*np.abs(rprimeLen - self.v*self.lifetime)/self.L
        mask = W>0.
        W = W[mask]
        
#        raise()

        
        I = np.zeros((x.shape[0], x.shape[1]))
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
        rprime = x - self.R[np.newaxis,np.newaxis,:]
        rprimeLen = np.linalg.norm(rprime, axis=-1)
                
        # Wavelet window, triangular: ___/\___
        W = 1.0 - 2.0*np.abs(rprimeLen - self.v*self.lifetime)/self.L
        mask = W>0.
        W = W[mask]
        
        G = np.zeros(x.shape)
        if(np.any(mask)):  # only do this if there is an active point
            print(mask)
            
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
            gradrprime = - rprime[mask]/np.sqrt(rprimeLen[mask])
            
            gradId = self.A*(np.sqrt(self.Rmax) + 0.5/np.sqrt(rprimeLen[mask]))
            gradId = gradId[:,np.newaxis] * gradrprime
            print("gradId", gradId.shape)
            gradIa = (self.dir - cosTheta*gradrprime)/rprimeLen[mask]
            print("gradIa", gradIa.shape)
            
            relpos = rprimeLen[mask] - self.v*self.lifetime
            gradW = np.where(relpos>0, -2.0/self.L, 0.0) # 0 at peak of np.abs
            gradW = np.where(relpos<0, +2.0/self.L, gradW)
            gradW = gradW * gradrprime
            print("gradW", gradW.shape)
            
    
            # chain rule the contributions
            Ia = Ia[:,np.newaxis]
            Id = Id[:,np.newaxis]
            W = W[:,np.newaxis]
            print("W", W.shape)
            print("G", G.shape)
            print("mask", mask.shape)
            print("G[mask]", G[mask[:,np.newaxis]].shape)
            G[mask[:,np.newaxis]] = (gradId*Ia + Id*gradIa)*W + Id*Ia*gradW
        
        return(G)
    