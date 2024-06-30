#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 13:31:16 2024

@author: zetadin
"""

import numpy as np
import pygame

from Brane import Brane
from Universe import updatables, drawables

class Entity():
    """
    An entity that can be simulated.
    It has position and velocity in world coordinates.
    Mixin, so can pass on constructor parameters to other superclasses.
    """
    def __init__(self, mass=1.0, drag=0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)  # forwards all unused arguments
        self.mass = mass
        self.dragCoef = drag
        
        # coordinates in world space
        self.r = np.zeros(2)
        self.v = np.zeros(2)
        self.a = np.zeros(2)
        
        self.parentBrane = None
        
    def update(self, dt: float):

        # force
        F = self.calcForce()
        
        # acelleration
        aNext = F/self.mass
        # drag

        aNext -= self.dragCoef * np.abs(self.v)*self.v
        # velocity verlet
        self.r += self.v*dt + 0.5*self.a
        self.v += 0.5*dt*(self.a+aNext)
        self.a = aNext
        
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
    def __init__(self, mass=50.0, drag=0.0):
        # superclass constructors
        super().__init__(mass, drag)
        
        # create a temp image that will be overriden
        self.img = pygame.Surface((16,16), flags=pygame.SRCALPHA)
        pygame.draw.rect(
                surface=self.img, color=(255, 0, 0, 255),
                rect=self.img.get_rect(),
                width=2, border_radius = 3)
        
        self.size = 16
        
        self.theta = 0.0 # direction in radians from North (Up)
        
                
    def draw(self, view):
        """
        Draw to screen
        """
        # culling
        if(view.isOnScreen(self)):
            # scale & rotate the image
            zoom = float(self.size)*view.zoom/self.img.get_width()
            surf = pygame.transform.rotozoom(
                    self.img,
                    -self.theta*180./np.pi, # in deg CCW of North (Up)
                    zoom)
            
            # update position on screen
            rect = surf.get_rect(center=view.transform(self.r))
            
            # draw to screen
            view.displaysurface.blit(surf, rect)
        

    def register(self, brane: Brane):
        """Add to the list of objects in the universe."""
        super().register(brane)
        drawables.add(self)
        
    def checkCollision(self, other: "SpriteEntity", dt):
        collided = False
            
        # Are they close enough and moving fast enough to collide on each axis?
        
        
        # line segment to circle collision
        # stationary circle by changingeffective velocity of self
        vdt = (self.v - other.v) * dt # start to end
        x   = self.r - vdt                   # start pos
        cx  = other.r - x         # start to center
        ce  = other.r - self.r    # end to center
                
        # end points in radius
        collision_radius = 0.5*(self.size+other.size)
        collision_radius_sq = collision_radius*collision_radius
        if(np.dot(cx,cx)<=collision_radius_sq):
            collided = True
        elif(np.dot(ce,ce)<=collision_radius_sq):
            collided = True
        # projection in segment?
        else:
            vdtsq = np.dot(vdt,vdt)
            u = np.dot(cx, vdt)/vdtsq
            if(u>=0.0 and u<=1.0):
                # check distance to center
                psq = u*u*vdtsq # (pos on start-end segment)^2
                dsq = np.dot(cx, cx) - psq # closest distance to center ^2
                if(dsq<=collision_radius_sq):
                    collided = True
    
        return(collided)