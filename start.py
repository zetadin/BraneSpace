import sys
import pygame
from pygame.locals import *

import numpy as np
import numpy.typing as npt


from Brane import Brane
from Universe import updatables, drawables
from View import View, HEIGHT, WIDTH, FPS
from entities.Entity import SpriteEntity
from entities.SimpleObjects import Ball
from entities.structures.Portal import Portal


view = View()
       
        
        
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
        drawables.add(self)
        updatables.append(self)
        
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

filler = SpriteEntity()
filler.r = np.array([5,5])
filler.register(cur_brane)


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
    
    