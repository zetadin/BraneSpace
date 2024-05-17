#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 09:57:06 2024

@author: zetadin
"""

import sys
sys.path.append("..") # enables entities import


from multiprocessing import Process, Queue, Value, Array
from entities.Entity import SpriteEntity
import numpy as np
import ctypes
from time import sleep



class ParallelSpriteEntity(SpriteEntity):
    """
    Entity update of which can be ofloaded to a subprocess.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #overwrite r,v with shared memory substitutes
        shared_arr = Array(ctypes.c_double, 2)
        r = np.frombuffer(shared_arr.get_obj())
        with shared_arr.get_lock():
            r[:] = self.r
            self.r = r
            
        shared_arr = Array(ctypes.c_double, 2)
        v = np.frombuffer(shared_arr.get_obj())
        with shared_arr.get_lock():
            v[:] = self.v
            self.v = v
                
    def update(self, dt: float):
        """Update with a random force so no need to ask Brane."""
        F = (np.random.random(2)-1.0)*0.1
        
        # acelleration
        aNext = F/self.mass
        # drag
        aNext -= self.dragCoef * np.abs(self.v)*self.v
        # velocity verlet
        self.r += self.v*dt + 0.5*self.a
        self.v += 0.5*dt*(self.a+aNext)
        self.a = aNext
        
        print("Updating: r=", self.r)
        
    def __getstate__(self):
        # pickle everything except the image for Queue insertion
        return {k:v for (k, v) in self.__dict__.items() if k!="img"}
    
    

class Worker(Process):
    def __init__(self, creationQueue, destructionQueue, **kwargs):
        super().__init__(**kwargs)
        self.creationQueue = creationQueue
        self.destructionQueue = destructionQueue
        
        self.myEntities = []
        

    def run(self):
        while(True):
            stop = False
            # read input
            while(not self.creationQueue.empty()):
                e = self.creationQueue.get()
                if(e != "STOP"):
                    self.myEntities.append(e)
                else:
                    stop=True
            
            # update the entities
            dt = 1.
            for e in self.myEntities:
                e.update(dt)
                
            # exit if asked to
            if(stop):
                del self.myEntities
                break
            
            sleep(0.02)
            
                    

def test_shared_memory():
    
    sharedEnt = ParallelSpriteEntity(mass=100.0, drag=0.3)
    sharedEnt.r[:] = [5.0,5.0]
    sharedEnt.v[:] = [0.01,-0.01]
    
    cQ = Queue()
    dQ = Queue()
    
    subprocess = Worker(cQ, dQ)
    subprocess.start()
    
    cQ.put(sharedEnt)
    
    sleep(0.1)
    print("Reading: r=", sharedEnt.r)
    cQ.put("STOP")
    cQ.close()
    dQ.close()
    subprocess.join()
    
    
    assert(np.all(sharedEnt.r != 5.0))