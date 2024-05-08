import sys
import pygame
from pygame.locals import *

import numpy as np
import numpy.typing as npt


pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

HEIGHT = 600
WIDTH = 600
FPS = 60

SIM_SIZE = 128

C = 8/1000.
W = 1000


FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BraneSpace")

# font
pygame.font.init()
serif_font = pygame.font.SysFont('liberationserif', 18)

# game object lists
all_sprites = pygame.sprite.Group()
updatable_sprites = pygame.sprite.Group()


class Wavelet:
    """
    Sinusoidal wavelet that terminates after one wave length.
    """
    def __init__(self,v: float, L: float, A: float, source: npt.ArrayLike):
        self.v = v
        self.L = L
        self.A = A
        self.R = source
        
        self.k = 2*np.pi/self.L
        self.w = self.v*self.k
        
        # lifetime
        self.maxLifetime = (SIM_SIZE + self.L)/self.v
        self.lifetime = 0
        self.parentBrane = None
        
    def register(self, parentBrane: "Brane"):
        # if already registered with a brane, move wavelet to new one
        if(self.parentBrane):
            self.parentBrane.wavelets.remove(self)
        parentBrane.wavelets.append(self)
        self.parentBrane = parentBrane
        
    def update(self, dt: float):
        self.lifetime += dt
        
        # remove wavelet after lifetime is over
        if(self.lifetime > self.maxLifetime):
            self.parentBrane = None
            self.parentBrane.wavelets.remove(self)
        
    def f(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Wavelet intencity everywhere in space.
        """
        rprime = x - self.R[np.newaxis,np.newaxis,:]
        distMat = np.sqrt(np.sum(rprime*rprime, axis=-1))
        # rprimeHat = rprime/distMat
        
        mask = np.logical_and(
                distMat <= self.v*self.lifetime,
                distMat >= max(0, self.v*self.lifetime - self.L)
                )
        I = np.zeros((SIM_SIZE, SIM_SIZE))
        I[mask] = self.A*np.sin(self.k*distMat[mask] + self.w*self.lifetime)
        return(I)
        
        
    def gradf(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Gradient of wavelet intencity everywhere in space.
        """
        rprime = x - R[np.newaxis,np.newaxis,:]
        distMat = np.sqrt(np.sum(rprime*rprime, axis=-1))
        
        mask = np.logical_and(
                distMat <= self.v*self.lifetime,
                distMat >= max(0, self.v*self.lifetime - self.L)
                )
        mask = mask[:,:,np.newaxis] # expand to cover the x and y

        G = np.zeros((SIM_SIZE, SIM_SIZE, 2))        
        G[mask] = self.A*np.cos(self.k*distMat[mask] + self.w*self.lifetime)
        G[mask]*= rprime[mask] * self.k/(2*distMat[mask])
        
        return(G)



class Brane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.I = np.zeros((SIM_SIZE, SIM_SIZE))
        self.I[16, 16] = 1.
        self.surf = pygame.Surface((2, 2)) # temporary
        self.surf.fill((128,128,128))
        self.rect = pygame.Rect(0,0,WIDTH,WIDTH)
        
        pos = np.arange(SIM_SIZE)
        self.coords = np.zeros((SIM_SIZE, SIM_SIZE, 2))
        self.coords[:,:,0] = np.repeat(pos[:,np.newaxis], SIM_SIZE, axis=1)
        self.coords[:,:,1] = np.repeat(pos[np.newaxis,:], SIM_SIZE, axis=0)
        
        self.elapsed = 0.
        
        self.wavelets=[]
        
        # add initial wavelet
        wl = Wavelet(v = 0.01, L=5.0, A=0.5, source=np.array([16.,16.]))
        wl.register(self)
        
    def register(self):
        # put into game object lists
        all_sprites.add(self)
        updatable_sprites.add(self)
        
        
    def update(self, dt: float):
        
        # update the intensity
        self.I = np.zeros((SIM_SIZE, SIM_SIZE))
        for wl in self.wavelets:
            wl.update(dt)
            self.I += wl.f(self.coords)
        
        
        # add a new wavelet every so often
        self.elapsed += dt
        if(self.elapsed > 1000):
            self.elapsed = 0.
            wl = Wavelet(v = 0.01, L=5.0, A=0.5, source=np.array([16.,16.]))
            wl.register(self)
            
            print(f"ms from last wavelet: {self.elapsed}\t live wavelets: {len(self.wavelets)}")
#            direction = (self.wf[16, 16]/np.abs(self.wf[16, 16]))
#            if(np.isnan(direction)):
#                direction = 1 + 0.j
#            self.wf[16, 16] += 0.25 * direction
            
            
        
        # re-paint the surface
        amp_arr = np.floor(np.clip(256*(self.I+1)/2, 0,255)).astype(np.uint8)
        amp_arr = np.repeat(amp_arr[:, :, np.newaxis], 3, axis=2)
        amp_surf = pygame.surfarray.make_surface(amp_arr)
        self.surf = pygame.transform.smoothscale(amp_surf, (WIDTH,WIDTH))



#class Brane(pygame.sprite.Sprite):
#    def __init__(self):
#        super().__init__()
#        
#        # self.amplitude = np.random.random((SIM_SIZE, SIM_SIZE))
#        # wf_r = np.sqrt(np.random.uniform(0, 1, (SIM_SIZE, SIM_SIZE)))
#        # wf_phase = np.exp(1.j * np.random.uniform(0, 2 * np.pi, (SIM_SIZE, SIM_SIZE)))
#        wf_r = np.zeros((SIM_SIZE, SIM_SIZE))
#        wf_r[16, 16] = 1.
#        wf_phase = 1 + 0.j
#        self.wf = wf_r * wf_phase
#        self.surf = pygame.Surface((2, 2)) # temporary
#        self.surf.fill((128,128,128))
#        self.rect = pygame.Rect(0,0,WIDTH,WIDTH)
#        
#        pos = np.arange(SIM_SIZE)
#        self.coords = np.zeros((SIM_SIZE, SIM_SIZE, 2))
#        self.coords[:,:,0] = np.repeat(pos[:,np.newaxis], SIM_SIZE, axis=1)
#        self.coords[:,:,1] = np.repeat(pos[np.newaxis,:], SIM_SIZE, axis=0)
#        
#        self.elapsed = 0.
#        
#        self.wavelets=[]
#        
#    def register(self):
#        # put into game object lists
#        all_sprites.add(self)
#        updatable_sprites.add(self)
#        
#        
#    def update(self, dt: float):
#        
#        # update the wavefunction forward in time
#        wf_new = np.zeros((SIM_SIZE, SIM_SIZE), dtype=np.complex128)
##        emission = np.absolute(self.wf)
#        
#        # loop over emissors
##        for i in range(SIM_SIZE):
##            for j in range(SIM_SIZE):
##                R = self.coords[i,j]
##                dist_mat = self.coords - R
##                dist_mat = np.sqrt(np.sum(dist_mat*dist_mat, axis=-1))
###                wf_new += self.wf[i,j] * np.exp(-W*1.j*dist_mat/C)
##                wf_new += emission[i,j] * np.exp(-W*1.j*dist_mat/C)
#        
#        R = self.coords[16,16]
#        dist_mat = self.coords - R
#        dist_mat = np.sqrt(np.sum(dist_mat*dist_mat, axis=-1))
#        wf_new += 0.5 * np.exp(-W*1.j*dist_mat/C)
#        self.wf = wf_new
#
#        # rotate phase
#        self.wf *= np.exp(-W*1.j*self.elapsed)
#        
#        # add some intensity every so often
#        self.elapsed += dt
#        if(self.elapsed > 1000):
#            print(self.elapsed)
#            self.elapsed = 0.
##            direction = (self.wf[16, 16]/np.abs(self.wf[16, 16]))
##            if(np.isnan(direction)):
##                direction = 1 + 0.j
##            self.wf[16, 16] += 0.25 * direction
#            
#            
#        
#        # re-paint the surface
##        amp_arr = np.real(self.wf)
#        amp_arr = np.absolute(self.wf)
##        print(amp_arr)
##        amp_arr = np.floor(255*amp_arr/np.max(amp_arr)).astype(np.uint8)
#        amp_arr = np.floor(np.clip(255*amp_arr/2, 0,255)).astype(np.uint8)
#        amp_arr = np.repeat(amp_arr[:, :, np.newaxis], 3, axis=2)
#        amp_surf = pygame.surfarray.make_surface(amp_arr)
#        self.surf = pygame.transform.smoothscale(amp_surf, (WIDTH,WIDTH))
        
        
        
# init objects        
cur_brane = Brane()
cur_brane.register()


# initial guess at frame time
dt = 1000./FPS


# game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
    # update objects
    for entity in updatable_sprites:
        entity.update(dt)
     
    # wipe screen 
    displaysurface.fill((0,0,0))
 
    # draw everything
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
 
    # show FPS
    fps_surface = serif_font.render(
            f"FPS: {FramePerSec.get_fps():.0f}",
            False, (180, 255, 150)
            )
    displaysurface.blit(fps_surface, (5,5))
    
    # push to frame buffer
    pygame.display.update()
    
    # wait for next frame
    dt = FramePerSec.tick(FPS)
    
#    if(cur_brane.elapsed>80):
#        sys.exit()
    
    