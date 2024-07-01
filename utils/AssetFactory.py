#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 12:30:55 2024

@author: zetadin
"""
import glob
import os
import pygame
import tqdm

class AssetFactory():
     def __init__(self):
         self.preloaded_imgs={}
         self.assets_path = os.path.join(os.getcwd(),"assets")
         
     def preloadAll(self):
         """
         Preload all recognised assets in the assets direcotry.
         """
         
         #images
         img_files = glob.glob(os.path.join(self.assets_path,"**","*.png"),
                               recursive=True)
         pbar = tqdm.tqdm(img_files)
         pbar.set_description("Loading Images")
         for f in pbar:
             _=self.loadImg(f, True)
         
     def loadImg(self, file: str, use_alpha: bool=True):
         key=file+"__use_alpha="+str(use_alpha)
         
         # return preloaded if possible
         if(key in self.preloaded_imgs.keys()):
             return(self.preloaded_imgs[key])
         
         # load it otherwise
         # convert path depending on the os
         if(os.name == 'nt'): # windows
             fp = os.path.join(self.assets_path, file).replace('/', '\\')
         else: # posix, java
             fp = os.path.join(self.assets_path, file).replace('\\','/')
         img = pygame.image.load(fp)
         
         if(use_alpha): # need transparency?
             img = img.convert_alpha()
         else:
             img = img.convert()
         # store preloaded
         self.preloaded_imgs[key]=img
         
         return(img)
         
     def registerProceduralImg(self, key, img):
         self.preloaded_imgs[key]=img
         
     def isLoadedImg(self, key):
         return(key in self.preloaded_imgs.keys())
         
     def loadProceduralImg(self, key: str):
         return(self.preloaded_imgs[key])
         
# exported objects:
assetFactory = AssetFactory()
