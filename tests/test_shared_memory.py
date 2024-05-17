#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 17 09:57:06 2024

@author: zetadin
"""

import sys
sys.path.append("..") # enables entities import


from multiprocessing import Process, Queue, set_start_method
from multiprocessing.shared_memory import SharedMemory
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
        self.r_shm = SharedMemory(create=True, size=self.r.nbytes)
        r = np.ndarray(shape=(2,), dtype=np.float64, buffer=self.r_shm.buf)
        r[:] = self.r[:]
        self.r = r
        
        self.v_shm = SharedMemory(create=True, size=self.v.nbytes)
        v = np.ndarray(shape=(2,), dtype=np.float64, buffer=self.v_shm.buf)
        v[:] = self.v[:]
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
        disregard=["img","r","v"]
        return {k:v for (k, v) in self.__dict__.items() if not k in disregard}
    
    def __setstate__(self, state):
        # store all attributes when unpickling
        self.__dict__.update(state)
        
        # add numpy arrays for SharedMemory regions
        self.r = np.ndarray(shape=(2,), dtype=np.float64, buffer=self.r_shm.buf)
        self.v = np.ndarray(shape=(2,), dtype=np.float64, buffer=self.v_shm.buf)
        
    def close(self):
        self.r_shm.close()
        self.v_shm.close()
        
    def unlink(self):
        self.r_shm.unlink()
        self.v_shm.unlink()
    
    

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
                    
            # exit if asked to
            if(stop):
                for e in self.myEntities:
                    # close shared memory for Worker process
                    e.close()
                    # tell GUI side to delete Entity as well
                    self.destructionQueue.put(e.drawablesKey)
                del self.myEntities
                break
            
            # update the entities
            dt = 1.
            for e in self.myEntities:
                e.update(dt)
            
            sleep(0.02)
            
                    

def test_shared_memory():
    
    set_start_method('fork')
        
    cQ = Queue()
    dQ = Queue()
    
    # create Process
    worker = Worker(cQ, dQ)
    worker.start()
    
    # create Entity
    sharedEnt = ParallelSpriteEntity(mass=100.0, drag=0.3)
    sharedEnt.r[:] = [5.0,5.0]
    sharedEnt.v[:] = [0.01,-0.01]
    
    # store Entity into dict of drawables
    drawables = {} # a dict with unique keys
    lastDrawablesKey = -1
    lastDrawablesKey+=1
    drawables[lastDrawablesKey] = sharedEnt
    sharedEnt.drawablesKey = lastDrawablesKey
    
    cQ.put(sharedEnt)
    del sharedEnt
    
    # wait and read new position
    sleep(0.1)
    print("Reading: r=", drawables[lastDrawablesKey].r)
    # check that we see position change in GUI process
    assert(np.all(drawables[lastDrawablesKey].r != 5.0))
    
    # stop Worker Process
    cQ.put("STOP")
    cQ.close()
    worker.join()
    
    # handle any events in the destruction Queue
    while(not dQ.empty()):
        key = dQ.get()
        # close shared memory for GUI side
        drawables[key].close()
        # free shared memory for GUI side
        drawables[key].unlink()
        # remove Entity from drawables
        del drawables[key]
    dQ.close()
    
    
    

    
    
    
if __name__ == "__main__":
    test_shared_memory()