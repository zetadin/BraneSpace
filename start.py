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

VV = 32/1000.
LL = 16


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
        self.maxLifetime = (SIM_SIZE*np.sqrt(2) + self.L)/self.v
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
            self.parentBrane.wavelets.remove(self)
            self.parentBrane = None
        
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
        I[mask] = self.A*np.sin(self.k*distMat[mask] - self.w*self.lifetime)
        I[mask] /= self.v*self.lifetime # Conserve intensity with time
        return(I)
        
        
    def gradf(self, x: npt.ArrayLike) -> npt.ArrayLike:
        """
        Gradient of wavelet intencity everywhere in space.
        """
        rprime = x - self.R[np.newaxis,np.newaxis,:]
        distMat = np.sqrt(np.sum(rprime*rprime, axis=-1))
        
        mask = np.logical_and(
                distMat <= self.v*self.lifetime,
                distMat >= max(0, self.v*self.lifetime - self.L)
                )
        mask = mask[:,:,np.newaxis] # expand to cover the x and y

        G = np.zeros((SIM_SIZE, SIM_SIZE, 2))        
        G[mask] = self.A*np.cos(self.k*distMat[mask] - self.w*self.lifetime)
        G[mask]*= rprime[mask] * self.k/(2*distMat[mask])
        G[mask] /= self.v*self.lifetime # Conserve intensity with time
        
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
        wl = Wavelet(v = VV, L=LL, A=2.5, source=np.array([16.,16.]))
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
            R = np.random.random((2))*SIM_SIZE
            wl = Wavelet(v = VV, L = LL, A=2.5, source=R)
            wl.register(self)
            
            print(f"ms from last wavelet: {self.elapsed}\t live wavelets: {len(self.wavelets)}")
        
        # re-paint the surface
        amp_arr = np.floor(np.clip(256*(self.I+1)/2, 0,255)).astype(np.uint8)
        amp_arr = np.repeat(amp_arr[:, :, np.newaxis], 3, axis=2)
        amp_surf = pygame.surfarray.make_surface(amp_arr)
        self.surf = pygame.transform.smoothscale(amp_surf, (WIDTH,WIDTH))


        
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
    
    