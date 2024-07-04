#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 18:30:32 2024

@author: zetadin
"""

from enum import Enum, auto


class GameMode(Enum):
    """
    What game mode are we running?
    TODO: selectable in start menu.
    """
    MENU = auto()
    ASTEROIDS = auto()
    #PIONEER = auto() # TODO

class PBC(Enum):
    """
    Periodic boundary conditions for the physics simulation.
    """
    NONE = auto()       # for PIONEER eventually
    TOROIDAL = auto()   # All sides warp
    
    
global pbc
pbc = PBC.NONE
global mode
mode = GameMode.ASTEROIDS
global curUniverseSize
curUniverseSize = None


global HEIGHT
HEIGHT = 600
global WIDTH
WIDTH = 600
FPS = 60