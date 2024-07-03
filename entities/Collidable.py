#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:01:10 2024

@author: zetadin
"""

import numpy as np
from entities.Entity import SpriteEntity
from Universe import updatables, drawables, collidables
from utils.Geometry import rotMat
import pygame

class Collidable(SpriteEntity):
    """
    These Entities have a collision radius which
    is used to detect collisions between them by
    Segment-Circle overlap crossing.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collisionRadius = 0.5*self.size
        
    
    def register(self, brane: "Brane"):
        """Add to the list of objects in the universe."""
        super().register(brane)
        collidables.append(self)
        
        
    def checkCollision(self, other: "Collidable", dt):
        """
        Do collision detection with another Collidable.
        """
        collided = False
            
        # TODO: fast filtering of many misses
        # Are they close enough and moving fast enough to collide on each axis?
        
        
        # line segment to circle collision
        # stationary circle by changing effective velocity of self
        vdt = self.dr - other.dr  # start to end
        x   = self.r - vdt        # start pos
        cx  = other.r - x         # start to center
        ce  = other.r - self.r    # end to center
                
        # end points in radius
        collision_radius = self.collisionRadius + other.collisionRadius
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
        
        
    def collidedWith(self, other):
        """Handles what happens after a collision."""
        pass;
        
        
    def destroy(self):
        """
        Destroy a collidable by removing all references to it.
        GC will eventually free the memory.
        If need for destruction becomes apparent during
        colision detection, destruction needs to be delayed until after
        detection is done. Hence collidable is marked for delayed destruction.
        Every collidable is responcible for it's own marking.
        """
        if self in collidables: collidables.remove(self)
        if self in updatables: updatables.remove(self)
        if self in drawables: drawables.remove(self)
        
        
    def draw(self, view):
        """
        Draw collision radius.
        """
        super().draw(view)
        
        # Debug shapes
        if(view.debug):    
            # rough collision circle
            collision_color = (168, 81, 245) # light purple
            pygame.draw.circle(view.displaysurface, collision_color,
                                   self.r,
                                   self.collisionRadius, 2)


class MultiPartCollidable(Collidable):
    """
    These Collidables don't need a finer shape for collision detection.
    They have multiple circular parts inside their outer collision radius.
    If collision on outer radius is detected, verify it with inner parts.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.part_rel_positions=np.array([[0,0]])
        self.part_radii=[self.collisionRadius]
        
    
    def checkCollision(self, other: "Collidable", dt):
        """
        Do collision detection with another Collidable.
        """
        # first try collision detection with outer radii
        collided = super().checkCollision(other, dt)
        
        if(collided): # check collision with any of the parts
            
            # find current positions of part centers
            rot_matrix = np.array([
                    [np.cos(self.theta),   np.sin(self.theta)],
                    [-np.sin(self.theta),  np.cos(self.theta)]])
            part_positions = self.r + np.matmul(self.part_rel_positions,
                                                rot_matrix)
            
            # find old positions of part centers
            rot_matrix = rotMat(self.theta - dt*self.rot_vel)
            old_part_positions = self.r-self.v*dt +\
                    np.matmul(self.part_rel_positions, rot_matrix)
                    
            # part velocities
            part_velocities = (part_positions - old_part_positions)/dt
            
            
            # loop through the parts
            for p in range(len(self.part_radii)):
                # make temporary unregistered Collidables to represent each
                c = Collidable()
                c.r = part_positions[p,:]
                c.v = part_velocities[p,:]
                c.collisionRadius = self.part_radii[p]
                
                # Check for collision using other's function.
                # If it is also multipart, this will allow part-part checks
                collided = other.checkCollision(c, dt)
                if(collided):
                    break # exit the loop early if collision is verified
    
        return(collided)
        
        
    def draw(self, view):
        """
        Draw part radii to screen.
        """
        super().draw(view)
        
        # Debug shapes
        if(view.debug):            
            # detailed collision circles
            rot_matrix = np.array([
                    [np.cos(self.theta),   np.sin(self.theta)],
                    [-np.sin(self.theta),  np.cos(self.theta)]])    
            screen_positions = self.r + np.matmul(self.part_rel_positions,
                                                  rot_matrix)
            collision_color = (74, 184, 212) # light blue
            for i in range(len(self.part_radii)):
                pygame.draw.circle(view.displaysurface, collision_color,
                                   screen_positions[i],
                                   self.part_radii[i], 2)