#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 11:22:18 2024

@author: zetadin
"""

import numpy as np
from BraneSpace.UI.View import View
from BraneSpace.core.Universe import Universe
from BraneSpace.entities.hazards.Asteroid import Asteroid
from time import time


def test_SlowDestroyRequested():
    # Init game state
    view = View()
    universe = Universe(view, parallel=False, braneSurfScale=4.0)
    
    N = 100
    destroy_fraction = 0.3
    
    # create asteroids
    for i in range(N):
        roid = Asteroid()
        roid.r = np.random.random(2)*1000
        roid.v = (np.random.random(2) - 0.5)*0.03
        roid.register(universe.brane)
    
    # chose asteroids to destroy
    index = np.arange(N)
    index = np.random.choice(index, int(N*destroy_fraction), replace=False)
    universe.destroy_these_collidables=[universe.collidables[i] for i in index]
    N_should_remain = N - int(N*destroy_fraction)
    
    # do the actual destruction
    start_t = time()
    universe.destroyRequested()
    elapsed_t = time() - start_t
    print(f"\nSlowDestroyRequested takes {elapsed_t*1.e6:.1f} mus")
    
    assert (len(universe.collidables) == N_should_remain)
    assert (len(universe.updatables) == N_should_remain+1) # Asteroids +1 Brane
    assert (len(universe.drawables) == N_should_remain+1)  # Asteroids +1 Brane
    
    
def test_FastDestroyRequested():
    # Init game state
    view = View()
    universe = Universe(view, parallel=False, braneSurfScale=4.0)
    
    N = 100
    destroy_fraction = 0.3
    
    # create asteroids
    for i in range(N):
        roid = Asteroid()
        roid.r = np.random.random(2)*1000
        roid.v = (np.random.random(2) - 0.5)*0.03
        roid.register(universe.brane)
    
    # chose asteroids to destroy
    index = np.arange(N)
    index = np.random.choice(index, int(N*destroy_fraction), replace=False)
    universe.destroy_these_collidables=[universe.collidables[i] for i in index]
    N_should_remain = N - int(N*destroy_fraction)
    
    # do the actual destruction
    start_t = time()
    universe.fastDestroyRequested()
    elapsed_t = time() - start_t
    print(f"\nFastDestroyRequested takes {elapsed_t*1.e6:.1f} mus")
    
    assert (len(universe.collidables) == N_should_remain)
    assert (len(universe.updatables) == N_should_remain+1) # Asteroids +1 Brane
    assert (len(universe.drawables) == N_should_remain+1)  # Asteroids +1 Brane
    