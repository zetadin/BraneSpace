import sys
import pygame
from pygame.locals import *

import numpy as np
import numpy.typing as npt


from Brane import Brane
from Universe import updatable_sprites, all_sprites
from View import View, HEIGHT, WIDTH, FPS


view = View()




class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # create transparent surface
        self.surf = pygame.Surface((10,10), flags=SRCALPHA) 
        pygame.draw.circle(
                surface=self.surf, color=(255, 0, 0, 255),
                center=(5,5), radius=5)
        
        self.mass = 1.0e2
        self.dragCoef = 0.1
        # coordinates in world space
        self.r = np.array([WIDTH/2, WIDTH/2])
        self.v = np.zeros(2)
        self.a = np.zeros(2)
        
        self.rect = self.surf.get_rect(center=self.r)
        
        self.parentBrane = None
        
    def update(self, dt: float):
        F = self.parentBrane.computeForceAt(self.r[np.newaxis,:])
        # remove the extra dimention used for multiple points
        F = np.squeeze(F, axis=0)
        
        # acelleration
        aNext = F/self.mass
        # drag
        aNext -= self.dragCoef * np.abs(self.v)*self.v
        # velocity verlet
        self.r += self.v*dt + 0.5*self.a
        self.v += 0.5*dt*(self.a+aNext)
        self.a = aNext
        
        
    def draw(self, screen):
        """
        Draw to screen
        """       
        # update position on screen
        self.rect = self.surf.get_rect(center=self.r)
        
        # draw to screen
        screen.blit(entity.surf, entity.rect)

    def register(self, brane: Brane):
        # put into game object lists
        all_sprites.add(self)
        updatable_sprites.add(self)
        
        self.parentBrane = brane
        
        
        
        
class Portal(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.img = pygame.image.load("assets/entities/structures/portal.png").convert_alpha()
        self.size = 128 # px
        
        self.mass = 1.0e9
        self.dragCoef = 20
        # coordinates in world space
        self.r = np.array([WIDTH*0.7, WIDTH*0.7])
        self.v = np.zeros(2)
        self.a = np.zeros(2)
        
        self.theta = 0.0 # direction in radians from North (Up)
        
        self.parentBrane = None
        
    def update(self, dt: float):
        F = self.parentBrane.computeForceAt(self.r[np.newaxis,:])
        # remove the extra dimention used for multiple points
        F = np.squeeze(F, axis=0)
        
        # acelleration
        aNext = F/self.mass
        # drag
        aNext -= self.dragCoef * np.abs(self.v)*self.v
        # velocity verlet
        self.r += self.v*dt + 0.5*self.a
        self.v += 0.5*dt*(self.a+aNext)
        self.a = aNext
        
        # spin ship for demo of rotation
        self.theta += 0.025*dt*np.pi
        
    def updateBrane(self, dt: float):
        """
        Update brane's intensity with local effects
        """
        pass
        
        
    def draw(self, screen):
        """
        Draw to screen
        """       
        # re-paint the surface from simulation
        zoom = float(self.size)/self.img.get_width()
        self.surf = pygame.transform.rotozoom(self.img, self.theta, zoom)
        
        # update position on screen
        self.rect = self.surf.get_rect(center=self.r)
        
        # draw to screen
        screen.blit(entity.surf, entity.rect)
        

    def register(self, brane: Brane):
        # put into game object lists
        all_sprites.add(self)
        updatable_sprites.add(self)
        
        self.parentBrane = brane
        
        
        
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.img = pygame.image.load("assets/entities/player/rocket.png").convert_alpha()
        self.size = 64 # px
        
        self.mass = 5.0e3
        self.dragCoef = 0.2
        # coordinates in world space
        self.r = np.array([WIDTH/3, WIDTH/3])
        self.v = np.zeros(2)
        self.a = np.zeros(2)
        
        self.theta = 0.0 # direction in radians from North (Up)
        
        self.parentBrane = None
        
    def update(self, dt: float):
        F = self.parentBrane.computeForceAt(self.r[np.newaxis,:])
        # remove the extra dimention used for multiple points
        F = np.squeeze(F, axis=0)
        
        # acelleration
        aNext = F/self.mass
        # drag
        aNext -= self.dragCoef * np.abs(self.v)*self.v
        # velocity verlet
        self.r += self.v*dt + 0.5*self.a
        self.v += 0.5*dt*(self.a+aNext)
        self.a = aNext
        
        # spin ship for demo of rotation
        self.theta -= 0.01*dt*np.pi

    def draw(self, screen):
        """
        Draw to screen
        """       
        # re-paint the surface from simulation
        zoom = float(self.size)/self.img.get_width()
        self.surf = pygame.transform.rotozoom(self.img, self.theta, zoom)
#        self.surf = pygame.transform.smoothscale(self.img, (self.size,self.size))
        
        # update position on screen
        self.rect = self.surf.get_rect(center=self.r)
        
        # draw to screen
        screen.blit(entity.surf, entity.rect)

    def register(self, brane: Brane):
        # put into game object lists
        all_sprites.add(self)
        updatable_sprites.add(self)
        
        self.parentBrane = brane
        
        
        
        
        
        
        
# init objects        
cur_brane = Brane()
cur_brane.register()

ball = Ball()
ball.register(cur_brane)

player = Player()
player.register(cur_brane)

portal = Portal()
portal.register(cur_brane)


# initial guess at frame time
dt = 1000./FPS


#
## fast forward
#for entity in updatable_sprites:
#    entity.update(2500)
    



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
    view.displaysurface.fill((0,0,0))
 
    # draw everything
    for entity in all_sprites:
        entity.draw(view.displaysurface)
 
    # show FPS
    fps_surface = view.serif_font.render(
            f"FPS: {view.FramePerSec.get_fps():.0f}",
            False, (180, 255, 150)
            )
    view.displaysurface.blit(fps_surface, (5,5))
    
    # push to frame buffer
    pygame.display.update()
    
    # wait for next frame
    dt = view.FramePerSec.tick(FPS)
    
#    if(cur_brane.elapsed>80):
#        sys.exit()
    
    