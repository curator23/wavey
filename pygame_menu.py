# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 19:38:58 2018

Pygame menu thingmy
@author: Washu
"""
import sys
import pygame
from pygame.locals import *


class Menu:
    def __init__(self, surfrect, icon):
        iconsize = 0.10
        self.selected = 0
        self.active = False
        self.rs = surface
        self.icon = icon
        self.items = []
        self.ricon =  pygame.Rect((0,0),(surfrect.w*iconsize,surfrect.w*iconsize))
        self.ricon.center = (surfrect.w-(surfrect.w*iconsize/2),surfrect.h-(surfrect.w*iconsize/2))
        
    def add(self, item):
        self.items.append(item)
    def draw(self):
        if self.active:
            if self.items.count == 0:
                self.active = False
            else:
                items = self.items
    def event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if self.active:
                for item in self.items:
                    
            if wave1['rects'][n].collidepoint(ev.pos):
                    touched = True
                    touch_id = n
                    pygame.mouse.get_rel()
            if rexit.collidepoint(ev.pos):
                pygame.quit()
                sys.exit()
        elif ev.type == pygame.MOUSEBUTTONUP:
            touched = False
class Item:
    def __init__(self):