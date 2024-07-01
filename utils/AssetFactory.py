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
         img_files = glob.glob(self.assets_path+"/**.png", recursive=True)
         print(img_files)
         pbar = tqdm.tqdm(img_files)
         pbar.set_description("Loading Images")
         for f in pbar:
             _=self.load_img(f, True)
         
     def load_img(self, file: str, use_alpha: bool=True):
         key=file+"__use_alpha="+str(use_alpha)
         
         # return preloaded if possible
         if(key in self.preloaded_imgs.keys()):
             return(self.preloaded_imgs[key])
         
         # load it otherwise
         img = pygame.image.load(os.path.join(self.assets_path, file))
         if(use_alpha):
                 img = img.convert_alpha()
         # store preloaded
         self.preloaded_imgs[key]=img
         return(img)
         
# exported objects:
assetFactory = AssetFactory()
