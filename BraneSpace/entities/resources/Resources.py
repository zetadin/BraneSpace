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
        self.size = 16 # px
        
        # physics properties
        self.mass = 1.0e2
        self.dragCoef = 0.05

        
    def addToPlayer(self, player: "Player"):
        """
        Set which Player property to increment.
        """
        # for now just put into the score
        player.score += 1
