# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 12:03:36 2018

@author: Washu
"""

import sys
import pygame
from pygame.locals import *
import pygame.mixer as mx
import pygame.mouse as ms

import numpy as np

class Control:
    def __init__(self, srf, pos=(0,0), size=(32,32), cols=((128,128,128),(160,192,192),(160,192,160)), img=None, dn_act=None, up_act=None, hd_act=None, vid=0, mode='click', img_brd=0.2):
        self.srf = srf
        self.pos = pos
        self.size = size
        self.cols = cols
        try:
            self.ncol = cols[0]
            self.ocol = cols[1]
            self.acol = cols[2]
        except IndexError:
            pass
        self.active = False
        self.dn_act = dn_act
        self.up_act = up_act
        self.hd_act = hd_act
        self.vid = vid
        
        self.over = False
        self.mpos = (0,0)
        self.mode = mode
        self.img_org = img
        self.set_size(size, img_brd)
        
    def set_pos(self, pos):
        self.pos = pos
        self.rect = pygame.Rect(pos,self.size)
        
    def set_size(self, size, img_brd=0.2):
        self.rect = pygame.Rect(self.pos,size)
        self.size = size
        self.img_brd = 1-img_brd
        self.img_crd = [self.pos[n] + int(size[n]*img_brd*0.5) for n in [0,1]]
        self.img_size = [int(size[n]*self.img_brd) for n in [0,1]]
        print(self.pos, size, self.img_crd, self.img_size)
        try:
            self.img = pygame.transform.scale(self.img_org,self.img_size)
        except Exception as e:
            print('couldn\'t resize image ', self.img_org, e)
            pass
       
    def draw_srf(self, srf):
        sr = srf.get_rect()
        cr = self.rect.clip(sr)
        if self.active:
            srf.fill(self.acol,cr)
            if self.over and len(self.cols)>3:
                srf.fill(self.cols[3],cr)
        elif self.over:
            srf.fill(self.ocol,cr)
        else:
            srf.fill(self.ncol,cr)
        try:
            #print("img: ",tuple(np.subtract(cr.center,self.img.center)))
            #print("img: ",self.img.get_rect().center)
            srf.blit(self.img,self.img_crd)#np.subtract(cr.center,self.img.get_rect().center))
        except Exception as e:
            #print(e)
            pass
    def draw(self):
        self.draw_srf(self.srf)
 
    def processEvent(self, ev):
        if self.active == False and ev.type == pygame.MOUSEBUTTONDOWN:
            if self.over == True:
                if self.mode == 'click':
                    self.active = True
                elif self.mode == 'toggle':
                    self.active = not self.active
                self.mpos = ms.get_pos()
                try:
                    self.dn_act(self.vid)
                except TypeError:
                    pass
        elif ev.type == pygame.MOUSEBUTTONUP:
            self.active = False
            if self.over == True:
                try:
                    self.up_act(self.vid)
                except TypeError:
                    pass
        return self.active
    
    def update(self):
        if self.active:
            try:
                self.hd_act(self.vid, np.subtract(ms.get_pos(), self.mpos))
            except TypeError:
                pass
            
        if self.rect.collidepoint(ms.get_pos()):
            if self.over == False:
                self.over = True
                #print("mouseover: ",self.vid, "; ",self.rect.center)
        else:
            if self.over == True:
                self.over = False
                #print("mouseoff: ",self.vid, "; ",self.rect.center)                
    
class CGroup:
    def __init__(self, size, pos, count):
        self.size = list(size)
        self.pos = list(pos)
        count = list(count)
        if count[0] != 0:    
            self.dir = 0
            self.count = count[0]
        else:
            self.dir = 1
            self.count = count[1]
        self.cons = {}
        self.fore = 0
        self.aft = 0

    def attach(self, con, name, end=False, link=False):
        self.cons[str(name)] = con
        size = self.size[self.dir]/self.count
        con.set_size((size,size))
        crd = [0]*2
        crd[1-self.dir] = self.pos[1-self.dir] + con.size[0]
        if end:
            crd[self.dir] = self.pos[self.dir] + self.size[self.dir] - (con.size[0]*(self.aft+1))
        else:
            crd[self.dir] = self.pos[self.dir] + (con.size[0]*self.fore)
        con.set_pos(crd)
        
    def draw(self):
        for con in cons:
            con.draw()