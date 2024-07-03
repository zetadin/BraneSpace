#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:07:40 2024

@author: zetadin
"""

import numpy as np
import pygame
from pygame.locals import *
from entities.Collidable import MultiPartCollidable
from entities.Entity import SpriteEntity
from wavelets.Tractor import Tractor
from View import HEIGHT, WIDTH
from Universe import universe
from utils.AssetFactory import assetFactory
from utils.Geometry import rotMat


class Player(MultiPartCollidable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.img = assetFactory.loadImg("entities/player/rocket.png", True)
        self.size = 64 # px
        self.collisionRadius = 0.5*self.size*1.1 # px
        
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
        self.collector_offset = 20.
        
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
        
        # collidable parts
        self.part_rel_positions = np.array([
                [0,-22],[0, 0], [-10,20],[10,20]
                ]) # x,y pairs
        self.part_radii = [10, 15, 12, 12]
        
        # attachments: things to draw and update besides the main sprite
        self.engine_flame = SpriteEntity("entities/player/rocket_thrust.png",
                                    size=20, visible=False)
        self.attachments=[self.engine_flame]
        self.attachment_rel_positions = np.array([
                [0, 35]
                ])
        
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
        
        # Update positions of attachments explicitly. No physics simulation.
        # Don't want them flying off or colliding with something for now.
        rm = rotMat(self.theta)
        attachment_rs = self.r + np.matmul(self.attachment_rel_positions, rm)
        for i,a in enumerate(self.attachments):
            a.theta = self.theta
            a.r = attachment_rs[i]
        
        
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
        collector_newr = self.r + self.collector_offset*self.direction
        self.collector_v = (collector_newr - self.collector_r)/dt
        self.collector_r = collector_newr
        
    def draw(self, view):
        """
        Draw to screen
        """
        super().draw(view)
        
        
        # only show engine flame if accelerating forward
        self.engine_flame.visible = self.fwd
        # draw attachemnts
        for a in self.attachments:
            a.draw(view)
        
        # Debug shapes
        if(view.debug):            
            pass

        
        
    def attemptPickUp(self, collectables: list, view: "View", dt: float):
        """Call after update() of all entities."""
        if(self.tractorActive):
            # compute collector velocity
            self.collector_v = self.v
            for e in collectables:
                e.attemptPickUp(self, view, dt)
        
        
    def collidedWith(self, other):
        """Handle collisions."""
        
        # what type of collidable did we run into?
        other_type = str(type(other))[2:-2].split('.')[-1]
        
        # Is it dangerous?
        if(other_type in ["Asteroid", "Explosion"]):
            # then game over
            universe.game_over = True
            
        # TODO: otherwize do a perfect eleastic collision
        # but only if both objects are still ok.
        # Return True here and do elastic collision
        # in Universe class if both objects return true
        
        
            