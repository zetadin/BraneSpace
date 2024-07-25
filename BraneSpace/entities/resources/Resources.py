#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:02:29 2024

@author: zetadin
"""

import numpy as np
import numpy.typing as npt

import BraneSpace.core.GlobalRules as GlobalRules
from BraneSpace.entities.Entity import SpriteEntity
from BraneSpace.utils.AssetFactory import assetFactory
from BraneSpace.utils.Geometry import expandPeriodicImages

class Collectable(SpriteEntity):
    """
    A SpriteEntity that can be picked up.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # forwards all unused arguments
        
    def register(self, brane: "Brane"):
        """Add to the list of objects in the universe."""
        super().register(brane)
        self.parentBrane.parentUniverse.collectables.append(self)
        
    def addToPlayer(self, player: "Player"):
        """
        Should be overwritten by children.
        Set which Player property to increment.
        """
        pass
        
    def attemptPickUp(self, player: "Player", view: "View", dt: float):
        # culling, can't pick up things far away anyway
        sucess = False
        if(view.isOnScreen(self)):
            
            # line segment to circle collision
            # stationary circle by changing velocity of Collectable
            vdt = self.dr - player.dr            # start to end
            x   = self.r - vdt                   # start pos
            
            # with PBC, check agains each image of collector
            # this is sufficient only if vdt < 0.5 * GlobalRules.curUniverseSize
            if(GlobalRules.pbc == GlobalRules.PBC.TOROIDAL):
                other_rs = expandPeriodicImages(player.collector_r,
                                                GlobalRules.curUniverseSize)
            else:
                other_rs = [player.collector_r]
                
            # loop through images. Stop when one collision found
            for otr in other_rs:
                cx  = otr - x         # start to center
                ce  = otr - self.r    # end to center
            
                # end points in radius
                if(np.dot(cx,cx)<=player.collect_radius_sq):
                    sucess = True
                    break
                elif(np.dot(ce,ce)<=player.collect_radius_sq):
                    sucess = True
                    break
                # projection in segment?
                else:
                    vdtsq = np.dot(vdt,vdt)
                    u = np.dot(cx, vdt)/vdtsq
                    if(u>=0.0 and u<=1.0):
                        # check distance to center
                        psq = u*u*vdtsq # (pos on start-end segment)^2
                        dsq = np.dot(cx, cx) - psq # closest distance to center ^2
                        if(dsq<=player.collect_radius_sq):
                            sucess = True
                            break
        
            if(sucess):
                # give to the player
                self.addToPlayer(player)
                
                # remove instance from object lists
                self.parentBrane.parentUniverse.collectables.remove(self)
                self.parentBrane.parentUniverse.updatables.remove(self)
                self.parentBrane.parentUniverse.drawables.remove(self)
                # this instance can now be garbage collected


class DarkMatter(Collectable):
    def __init__(self):
        super().__init__()
        
        # create/load image
        self.img = assetFactory.loadImg("entities/resources/dark_matter.png", True)
        # needs to be a local copy to allow per-resource alpha
        self.img = self.img.copy() 
        self.size = 16 # px
        
        # physics properties
        self.mass = 1.0e2
        self.dragCoef = 0.05
        
        # decay properties
        self.maxLifeTime = 10000 + np.random.random()*5000. # ms; 10-15 s
        self.curLifeTime = 0   # ms
        
        self.blink_factor_start = 0.8 # when blinking starts
        self.blink_times = 5          # how many blinks
        self.half_blink_period = (1.-self.blink_factor_start)/(self.blink_times*2-1)
        self.invis_blink_increase_start = self.blink_factor_start - self.half_blink_period 
        
        
    def update(self, dt: float):
        super().update(dt)
        
        # lifetime
        self.curLifeTime += dt
        if(self.curLifeTime > self.maxLifeTime):
            # safe to destroy here: we are outside universe.collisionDetect()
            # remove instance from object lists
            self.parentBrane.parentUniverse.collectables.remove(self)
            self.parentBrane.parentUniverse.updatables.remove(self)
            self.parentBrane.parentUniverse.drawables.remove(self)
            return
        
        # check if we should be blinking
        factor = self.curLifeTime/self.maxLifeTime
        if(factor>self.blink_factor_start):
            # Change variables so b=0 at start of first blink (rising).
            # This rising part of the first blink is invisible.
            # And b=1 at end of last blink (falling)
            b = (factor - self.invis_blink_increase_start)/(1.-self.invis_blink_increase_start)
            
            # calculate new alpha value by modulus
            alpha = np.fmod(b * self.blink_times, 1.) # progress of a blink: 0 to 1
            alpha = int((1 - np.abs(alpha*2 - 1))*256) # alpha: 256 -> opaque
            if(alpha<1):
                # clamp alpha so mask below always works, even after image
                # should have gone completely transparent
                alpha = 1
#            print(f"factor={factor:.2f}, b={b:.2f}, alpha={alpha}")
        
            # overwrite img's alpha
            img_a = np.array(self.img.get_view('A'), copy=False)
            img_a[img_a>0] = alpha
            del img_a # to unlock img and allow blit

        
    def addToPlayer(self, player: "Player"):
        """
        Set which Player property to increment.
        """
        # for now just put into the score
        player.score += 1
