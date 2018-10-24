#import pygame_sdl2
#pygame_sdl2.import_as_pygame()
import sys
import pygame
from pygame.locals import *
import pygame.mixer as mx
import pygame.mouse as ms

import numpy as np
from scipy.io import wavfile


points=256

square_scale = 10
damping = 0.995
force = 0.75

wave1 = {}
wave1['tar'] = np.zeros(shape=(points,2),dtype=float)
wave1['pos'] = np.zeros(shape=(points,2),dtype=float)
wave1['vel'] = np.zeros(shape=(points,2),dtype=float)
wave1['acc'] = np.zeros(shape=(points,2),dtype=float)
wave1['mask']= np.zeros(shape=(points,1),dtype=float)
wave1['mask'][0] = 1
wave1['mask'][-1] = 1
wave1['rsel'] = []

wave1['rects'] = []
wave1['raux'] = []

fade_time = 20
#pygame.init()
# Resolution is ignored on Android
surface = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
surfrect = surface.get_rect()

#sdata[0]=255
mx.init()
parp=mx.Sound('h:/parp.wav')
parp.play()

sdata = np.copy(wave1['pos'][...,0]*2*np.pi)

'''
sdata = np.sin(sdata)*1000


sound = [mx.Sound(array=sdata.data),mx.Sound(array=sdata.data),mx.Sound(array=sdata.data)]
sdx = 0
sdx2 = 1
sdx3 = 2
sound[sdx].play(loops=-1, fade_ms=fade_time)
'''

for n in range(points):
    posx=(1+n)/(points+1)
    wave1['tar'][n,0] = posx
    wave1['pos'][n,0] = posx
    
    wr = pygame.Rect((0,0),(surfrect.w/points,surfrect.w/points))
    wave1['rects'].append(wr)
    
    sr = pygame.Rect((0,0),(surfrect.w/points,surfrect.h * 0.7))
    sr.x = (surfrect.w*(wave1['pos'][n,0] ))
    sr.y = surfrect.h* 0.15
    wave1['rsel'].append(sr)
    
    ar = pygame.Rect((0,0),(surfrect.w/points,surfrect.w/points))
    ar.x = (surfrect.w*(wave1['pos'][n,0] ))
    ar.y = surfrect.h* 0.15
    wave1['raux'].append(ar)
    
touched = False
touch_id = 0

control = False
cval = 0.95

rexit = pygame.Rect((0,0),(64,64))
rmenu = pygame.Rect((0,0),(64,64))
rmenu.center = (surfrect.w-32,32)
rlctl = pygame.Rect((0,0),(64,64))
rlctl.center = (32,surfrect.h-32)
while True:
    
    if not touched:
        touch_id = -1
        for n in range(points):
            if wave1['rsel'][n].collidepoint(ms.get_pos()):
                touch_id = n
                
    for ev in pygame.event.get():
        if ev.type == QUIT:
            pygame.quit()
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if rmenu.collidepoint(ev.pos):
                print('writing:', sdata.size)
                sdata = sdata/np.max(sdata)
                wavfile.write("foop.wav",22050,sdata)
                sdata = np.copy(wave1['pos'][...,0]*2*np.pi)
            if touch_id >= 0:
                touched = True
                pygame.mouse.get_rel()
            if rexit.collidepoint(ev.pos):
                pygame.quit()
                sys.exit()
            if rlctl.collidepoint(ev.pos):
                control = True
                pygame.mouse.get_rel()
        elif ev.type == pygame.MOUSEBUTTONUP:
            touched = False
            control = False
            
    clock.tick(60)
    
    surface.fill((0, 0, 0))
    surface.fill((128,0,0),rexit)    
    surface.fill((0,0,128),rmenu)    
    surface.fill((0,128,128),rlctl)    
    
    if touched:
        pos = wave1['pos'][touch_id]
        vel = pygame.mouse.get_rel()
        pos = pos+vel
        pos[0] = wave1['tar'][touch_id,0]
        wave1['pos'][touch_id] = pos
        wave1['vel'][touch_id][1] = vel[0]
        wave1['vel'][touch_id][0] = 0
        print("id:",touch_id," x:",pos[0]," y:",pos[1])
        #print

    wave1['acc'].fill(0)
    
        
    
    for n in range(1,points):
        dd = (wave1['pos'][n-1] - wave1['pos'][n]) * force
#        dd = np.sign(dd)*dd*dd
        dd[0] = 0;
        wave1['acc'][n] = wave1['acc'][n]+dd
        wave1['acc'][n-1] = wave1['acc'][n-1]-dd

    wave1['acc'] = wave1['acc']+(wave1['tar'] - wave1['pos']) * force * wave1['mask']
        
    wave1['vel'] = wave1['vel'] + wave1['acc']
    wave1['vel'] = wave1['vel'] * damping
    wave1['pos'] = wave1['pos'] + wave1['vel']
    if control:
        wave1['pos'][...,1] = wave1['pos'][...,1] * cval
        wave1['vel'][...,1] = wave1['vel'][...,1] * cval
        wave1['acc'][...,1] = wave1['acc'][...,1] * cval
    pm = np.abs(wave1['acc'][:,1]).max()
    vm = np.abs(wave1['vel'][:,1]).max()
    if vm < 0:
        vscale = np.abs(wave1['acc'][:,1]).max()/np.abs(wave1['vel'][:,1]).max()
    else:
        vscale = 1
    aux_val = np.sqrt(wave1['acc'][:,1]**2 + (vscale*wave1['vel'][:,1])**2)
    for n in range(points):
 
        wr = wave1['rects'][n]
        wr.x = (surfrect.w*(wave1['pos'][n,0] ))
        wr.y = (surfrect.h*(0.5)+wave1['pos'][n,1])
        #if n==0:
            #print("x:",wr.x," y:",wr.y)
            #print(" x:",wave1['pos'][n,0]," y:",wave1['pos'][n,1])
        if touch_id == n:
            surface.fill((40,64,4), wave1['rsel'][n])
            if touched:
                surface.fill((140,255,40), wr)
            else:
                surface.fill((112,192,0), wr)
        else:
            surface.fill((128,255,0), wr)
        
        ar = wave1['raux'][n]
        ar.x = (surfrect.w*(wave1['pos'][n,0] ))
        ar.y = (surfrect.h*(0.15) + aux_val[n])    
        surface.fill((128,128,0), ar)
        
    pygame.display.flip()

    sdata = np.append(sdata, wave1['pos'][...,1])
'''
    np.copyto(sdata,wave1['pos'][...,1]*255)
    sound[sdx].fadeout(fade_time)
    sound[sdx2].play(loops=-1, fade_ms=fade_time)
    sound[sdx3] = mx.Sound(array=sdata.data)
    
    sdx = (sdx+1)%3
    sdx2 = (sdx2+1)%3
    sdx3 = (sdx3+1)%3
'''    