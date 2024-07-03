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
    