#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 11:52:25 2024

@author: zetadin
"""
import numpy as np


def rotMat(theta):
    return (np.array([[np.cos(theta),   np.sin(theta)],
                      [-np.sin(theta),  np.cos(theta)]]))


# cached periodic expansion array. Created only once.
shift_arr = np.array([[-1,-1],[-1,0],[-1,1],
                      [0,-1], [0,0], [0,1],
                      [1,-1], [1,0], [1,1]])
    
def expandPeriodicImages(r, uniSize):
    """
    Expand coordintes into their periodic images.
    """
    return(r[np.newaxis,:] + shift_arr*uniSize)