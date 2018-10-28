# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 14:52:28 2018

encapsulates a simulation of a 2d wave field with oscillation limeted to the 3rd dimension

@author: mecme
"""

import sys
import pygame
from pygame.locals import *
import pygame.mixer as mx
import pygame.mouse as ms
import pygame.time as t

import numpy as np
import scipy.signal as sgn
import matplotlib.pyplot as pp



class Wavegrid:
    INT_NONE = 0
    INT_TRAP = 1
    INT_POLY = 2
    
    def __init__(self, size=(50,50), force=1, damp=0.1, edgecase=('None','None','None','None'), integrator=0, filter_size=1, filter_width=1):
        self.size = size
        self.force = force
        self.damp = damp
        self.edgecase = edgecase
        
        self.pos = np.zeros(size)
        self.vel = np.zeros(size)
        self.acc = np.zeros(size)
        self.tar = np.zeros(size)
        self.mas = np.ones(size)
        self.drg = np.full(size,float(damp))
        
        self.make_filter(filter_size, filter_width)
        
        self.integrator = integrator
        
    def make_filter(self, filter_size, filter_width):
        self.filter_size = filter_size 
        self.filter_width = filter_width
        
        self.flt = sgn.gaussian(1+self.filter_size*2,self.filter_width)
        self.flt = self.flt.reshape((-1,1))*self.flt.reshape((1,-1))
        
        self.flt[filter_size,filter_size] = 0
        self.flt = np.sqrt(self.flt)
        self.flt = self.flt / self.flt.sum()
        
        self.flt = self.flt / self.flt.sum()
        
        
    def update(self, timestep=1):
        if self.integrator == self.INT_NONE:
            #the force is proportional to the displacement from the average position of its neighbors
            self.tar = sgn.correlate2d(self.pos,self.flt,mode='same')
            self.acc = (( self.tar - self.pos ) * self.force/self.mas )

            #integrate acc to vel            
            self.vel = self.vel + self.acc
            
            #dampen velocity
            self.vel = self.vel * (1-self.drg)
            
            #integrate vel to pos
            self.pos = self.pos + self.vel
            
            
        elif self.integrator == self.INT_TRAP:
            pass
        else:
            pass
        
        
        
    
    
print('\ntesting Wavegrid...\n')
wavey = Wavegrid()

print('filter:\n',wavey.flt)

wavey.pos[24:26,24:26] = np.full((2,2),1)

def plot():
    wavey.update()
    #pp.contour(wavey.pos)
    pp.pcolormesh(wavey.pos)
    pp.show()
    
    

    
while True: #False: #
    plot()
    t.delay(100)