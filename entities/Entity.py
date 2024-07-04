#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:31:16 2024

@author: zetadin
"""

import numpy as np
import pygame

import GlobalRules
from Brane import Brane
from Universe import updatables, drawables
from utils.AssetFactory import assetFactory

class Entity():
    """
    An entity that can be simulated.
    It has position and velocity in world coordinates.
    Mixin, so can pass on constructor parameters to other superclasses.
    """
    def __init__(self, mass=1.0, drag=0.0,
                 r = np.zeros(2), v = np.zeros(2), a = np.zeros(2),
                 *args, **kwargs):
        super().__init__(*args, **kwargs)  # forwards all unused arguments
        self.mass = mass
        self.dragCoef = drag
        
        # coordinates in world space
        self.r = r
        self.v = v
        self.a = a
        self.dr = np.zeros(2) # change in r in this time step
        
        # warp r into primary box image
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            self.r = np.fmod(self.r, GlobalRules.curUniverseSize)
            self.r[self.r<0] += GlobalRules.curUniverseSize
        
        self.parentBrane = None
        
    def update(self, dt: float):

        # force
        F = self.calcForce()
        
        # acelleration
        aNext = F/self.mass
        # drag

        aNext -= self.dragCoef * np.abs(self.v)*self.v
        # velocity verlet
        self.dr = self.v*dt + 0.5*self.a
        
        
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            # limit movement to 1/4 a periodic box/update
            self.dr = np.clip(self.v*dt + 0.5*self.a,
                              -0.25*GlobalRules.curUniverseSize,
                              0.25*GlobalRules.curUniverseSize)

        self.v += 0.5*dt*(self.a+aNext) # drag limits max v
        
        self.r += self.dr
        self.a = aNext
        
        if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
            self.r = np.fmod(self.r, GlobalRules.curUniverseSize)
            self.r[self.r<0] += GlobalRules.curUniverseSize
        
    def calcForce(self):
        F = self.parentBrane.computeForceAt(self.r[np.newaxis,:])
        # remove the extra dimention used for multiple points
        F = np.squeeze(F, axis=0)
        return(F)

    def register(self, brane: Brane):
        """Add to the list of objects in the universe."""
        updatables.append(self)
        self.parentBrane = brane
        
        
        
class SpriteEntity(Entity, pygame.sprite.Sprite):
    """
    An entity that gets drawn on sceen.
    """
    def __init__(self, img_file=None, visible=True, size=16,
                 theta=0.0, rot_vel=0.0,
                 *args, **kwargs):
        # superclass constructors
        super().__init__(*args, **kwargs)
        
        # create a temp image that will be overriden
        if(not img_file is None):
            self.img = assetFactory.loadImg(img_file, True)
        else:
            self.img = None
        
        self.visible = visible
        self.size = size
        
        self.theta = theta # direction in radians from North (Up)
        self.rot_vel = rot_vel # rotational velocity
        
        
    def update(self, dt: float):
        super().update(dt)
        #rotation
        self.theta -= dt*self.rot_vel
        
                
    def draw(self, view):
        """
        Draw to screen.
        Supports PBC.
        """
        # culling
        if(view.isOnScreen(self)):
             # check if image surface was created
            if(not self.img is None and self.visible):
                # scale & rotate the image
                zoom = float(self.size)*view.zoom/self.img.get_width()
                surf = pygame.transform.rotozoom(
                        self.img,
                        -self.theta*180./np.pi, # in deg CCW of North (Up)
                        zoom)
                
                if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
                    # find visible periodic images and their coords
                    vis, pos = view.periodicImagesOnScreen(self)
                    for i in range(vis.shape[0]):
                        if(vis[i]): # check visibility of each image
                            # draw that image to screen
                            view.drawSurfToView(surf, pos[i])
                    self.periodic_images = (vis,pos)
                    
                else:
                    # draw single image to screen
                    view.drawSurfToView(surf, self.r)
        

    def register(self, brane: Brane):
        """Add to the list of objects in the universe."""
        super().register(brane)
        drawables.add(self)
