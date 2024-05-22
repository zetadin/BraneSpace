#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:07:40 2024

@author: zetadin
"""

import numpy as np
import pygame
from pygame.locals import *
from entities.Entity import SpriteEntity
from wavelets.Tractor import Tractor
from View import HEIGHT, WIDTH


class Player(SpriteEntity):
    def __init__(self):
        super().__init__()
        self.img = pygame.image.load("assets/entities/player/rocket.png").convert_alpha()
        self.size = 64 # px
        
        # physics properties
        self.mass = 5.0e3
        self.dragCoef = 0.02
        # coordinates in world space
        self.r = np.array([WIDTH/3, WIDTH/3])
        self.theta = -np.pi*0.5
        
        self.tractorElapsed = 0.0
        self.tractorActive = True
        self.collect_radius = 5.
        self.collect_radius_sq = self.collect_radius*self.collect_radius
        
        self.score = 0
        
        self.rot_speed = np.pi/2000. # 180 deg in 1 sec        
        self.rotationDirection = 0.0
        
        self.fwdThrust = 2.0 # Newtons
        self.bckThrust = 0.50  # Newtons
        
        self.fwd = False
        self.bck = False
        
        # collector motion
        direction = np.array([-np.sin(self.theta), -np.cos(self.theta)])
        self.collector_r = self.r + self.collect_radius*direction
        self.collector_v = np.zeros(2)
        
    def calcForce(self):
        F = self.parentBrane.computeForceAt(self.r[np.newaxis,:])
        # remove the extra dimention used for multiple points
        F = np.squeeze(F, axis=0)
        
        if(self.fwd):
            direction = np.array([-np.sin(self.theta), -np.cos(self.theta)])
            F += direction * self.fwdThrust
        if(self.bck):
            direction = np.array([-np.sin(self.theta), -np.cos(self.theta)])
            F -= direction * self.bckThrust
        
        return(F)
        
    def update(self, dt: float):
        super().update(dt)
        
        # update ship rotation        
        self.theta += dt*self.rot_speed*self.rotationDirection
        
        # every L/(2*v) seconds emit a tractor wavelet
        self.tractorElapsed += dt
        pulseTime = 8.0*0.5/3.2e-2
        if(self.tractorElapsed > pulseTime):
            self.tractorElapsed -= pulseTime
            
            # where the beam is heading
            direction = np.array([-np.sin(self.theta), -np.cos(self.theta)])
            # source of the wave in sim coords
            # a bit forward of player ship
            start = self.r/self.parentBrane.surfScale + 3*direction 
            wl = Tractor(source=start, direction=direction,
                         v = 3.2e-2,
                         L = 8.0,
                         A = 0.1,
                         Rmax = 128./self.parentBrane.surfScale, # in sim coords
                         debug=False)
            wl.alive = self.tractorElapsed
            wl.register(self.parentBrane)
        
        
        # collector motion
        direction = np.array([-np.sin(self.theta), -np.cos(self.theta)])
        collector_newr = self.r + self.collect_radius*direction
        self.collector_v = (collector_newr - self.collector_r)/dt
        self.collector_r = collector_newr
        
        
    def attemptPickUp(self, collectables: list, view: "View", dt: float):
        """Call after update() of all entities."""
        if(self.tractorActive):
            # compute collector velocity
            self.collector_v = self.v
            for e in collectables:
                e.attemptPickUp(self, view, dt)
        
        
            