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
from utils.AssetFactory import assetFactory


class Player(SpriteEntity):
    def __init__(self):
        super().__init__()
        self.img = assetFactory.load_img("entities/player/rocket.png", True)
        self.size = 64 # px
        
        # physics properties
        self.mass = 5.0e3
        self.dragCoef = 0.02
        # coordinates in world space
        self.r = np.array([WIDTH/2, WIDTH/2])
        self.theta = 0 #np.pi*0.5
        
        self.tractorElapsed = 0.0
        self.tractorActive = True
        self.collect_radius = 10.
        self.collect_radius_sq = self.collect_radius*self.collect_radius
        
        self.score = 0
        
        self.rot_speed = np.pi/2000. # 180 deg in 1 sec        
        self.rotationDirection = 0.0
        
        self.fwdThrust = 2.0 # Newtons
        self.bckThrust = 0.50  # Newtons
        
        self.fwd = False
        self.bck = False
        
        self.tractor = False
        
        # collector motion
        self.direction = np.array([np.sin(self.theta), -np.cos(self.theta)])
        self.collector_r = self.r + self.collect_radius*self.direction
        self.collector_v = np.zeros(2)
        
    def calcForce(self):
        F = self.parentBrane.computeForceAt(self.r[np.newaxis,:])
        # remove the extra dimention used for multiple points
        F = np.squeeze(F, axis=0)
        

        if(self.fwd):
            F += self.direction * self.fwdThrust
        if(self.bck):
            F -= self.direction * self.bckThrust
        
        return(F)
        
    def update(self, dt: float):
        # facing unit vector
        self.direction = np.array([np.sin(self.theta), -np.cos(self.theta)])
        super().update(dt)
        
        # update ship rotation        
        self.theta += dt*self.rot_speed*self.rotationDirection
        
        
        
        # every L/(2*v) seconds emit a tractor wavelet
        if(self.tractor):
            self.tractorElapsed += dt
            pulseTime = 8.0*0.5/3.2e-2
            if(self.tractorElapsed > pulseTime):
                self.tractorElapsed -= pulseTime
                
                # source of the wave in sim coords
                # a bit forward of player ship
                start = (self.r + 20*self.direction)/self.parentBrane.surfScale
                wl = Tractor(source=start, direction=self.direction,
                             v = 3.2e-2,
                             L = 8.0,
                             A = 0.1,
                             Rmax = 128./self.parentBrane.surfScale, # in sim coords
                             debug=False)
                wl.alive = self.tractorElapsed
                wl.register(self.parentBrane)
        
        
        # collector motion
        collector_newr = self.r + self.collect_radius*self.direction
        self.collector_v = (collector_newr - self.collector_r)/dt
        self.collector_r = collector_newr
        
    def draw(self, view):
        """
        Draw to screen
        """
        super().draw(view)
        
#        # Debug shapes
#        # collector zone
#        pygame.draw.circle(view.displaysurface, (0,0,255),
#                           (self.collector_r[0],
#                            self.collector_r[1]),
#                           self.collect_radius
#                          )
#                           
#        # collector velocity
#        L = np.ceil(np.linalg.norm(self.collector_v)*500)
#        collector_vel = pygame.Surface((6, L), flags=pygame.SRCALPHA)
#        pygame.draw.polygon(collector_vel, (0,255,0),
#                           #((2,L),(2,2), (0,2),(3,0),(5,2), (3,2),(3,L)),
#                           ((0,L),(3,0),(5,L)),
#                           width = 2
#                          )
#        angle = np.arctan(self.collector_v[0]/-self.collector_v[1])
#        if(self.collector_v[1]>0): # compensate for period of tan
#            angle+=np.pi
#        collector_vel = pygame.transform.rotozoom(
#                collector_vel,
#                -angle*180/np.pi, # in deg CCW
#                1
#                )
#        rect = collector_vel.get_rect(center=view.transform(self.collector_r))
#        view.displaysurface.blit(collector_vel, rect)
        
        
    def attemptPickUp(self, collectables: list, view: "View", dt: float):
        """Call after update() of all entities."""
        if(self.tractorActive):
            # compute collector velocity
            self.collector_v = self.v
            for e in collectables:
                e.attemptPickUp(self, view, dt)
        
        
            