#import pygame_sdl2
#pygame_sdl2.import_as_pygame()
import sys
import pygame
from pygame.locals import *
import pygame.mixer as mx
import pygame.mouse as ms
import pygame.time as t

import numpy as np
import scipy.signal as sgn


from pygame_control import Control

from resources import *

#number of samples to process
points=128

#global physics parmeters
damping = 0.9995
force = 1
extra_distance = 1
end_damping = [0.0,1.0]

#message system
class Message:
    def __init__(self, msg, crd=[0,0] ):
        self.msg = msg
        self.crd = list(crd)
        
    def showValue(self, name, value):
        self.msg = str(name) + ": " + str(value)
    
msg = Message('...............Wavey.py',(80,12))



#a dictionary of per sample parameters
wave1 = {}
wave1['tar'] = np.zeros(shape=(points,2),dtype=float)
wave1['pos'] = np.zeros(shape=(points,2),dtype=float)
wave1['vel'] = np.zeros(shape=(points,2),dtype=float)
wave1['acc'] = np.zeros(shape=(points,2),dtype=float)
wave1['mask']= np.zeros(shape=(points,1),dtype=float)
wave1['mask'][0] = 1
wave1['mask'][-1] = 1


kernel_width = 20
kernel_depth = 20
kernel1 = sgn.gaussian(1+kernel_width*2,2)
kernel1 = kernel1/kernel1.sum()

kernel2 = sgn.gaussian(1+kernel_width*2,1)
kernel2 = kernel2/kernel2.sum()
#kernel2[kernel_width+1] = 0

def initWaveRender(wave, points):
    global surfrect
    
    wave1['rsel'] = []
    wave1['rects'] = []
    wave1['raux'] = []
    size = (max(1,surfrect.w/points), max(3, surfrect.h * 0.01, surfrect.w/points))
    
    for n in range(points):
        posx=(n)/(points)
        wave1['tar'][n,0] = posx
        wave1['pos'][n,0] = posx
        
        wr = pygame.Rect((0,0),size)
        wave1['rects'].append(wr)
        
        sr = pygame.Rect((0,0),(size[0],surfrect.h * 0.7))
        sr.x = (surfrect.w*(wave1['pos'][n,0] ))
        sr.y = surfrect.h* 0.15
        wave1['rsel'].append(sr)
        
        ar = pygame.Rect((0,0),size)
        ar.x = (surfrect.w*(wave1['pos'][n,0] ))
        ar.y = surfrect.h* 0.15
        wave1['raux'].append(ar)

def resize_kernel(width, depth, points):
    kw = max(min(width,1)*points,3)
    if int(points/2):
        kw = points
    else:
        kw = points-1
    kd = max(min(1,depth) * kw,0.5)

    kernel2 = sgn.gaussian(kw,kd)
    kernel2 = kernel2/kernel2.sum()
    print("kd,kw: ",kd,kw)

    
def resampleWave(wave, points):
    mval =  wave['tar'][:,0].size / points
    wave['tar'] = sgn.resample(wave['tar'], points)
    
    wave['pos'] = sgn.resample(wave['pos'], points)
    wave['vel'] = sgn.resample(wave['vel']*mval, points)
    wave['acc'] = sgn.resample(wave['acc'], points)
    wave['mask']= np.zeros(shape=(points,1),dtype=float)
    wave['mask'][0] = 1
    wave['mask'][-1] = 1
    resize_kernel(kernel_width/100, kernel_depth/100, points)
    

def lerp(x, y, a):
    return (x-y)*a + y
"""
xa +y(1-a)
xa -y(a-1)
xa -ay + y
(x-y)a +y
"""

times = {}
#macro for limiting event occurence
def timer(stamp_name, rate=1000):
    time = t.get_ticks()
    if (time-times[stamp_name]) > rate:
        times[stamp_name] = time
        return True
    return False

#timer for tracking things like print repeat intervals
times['touch_printer'] = t.get_ticks()
times['param_printer'] = t.get_ticks()


def getButtonColors(hue):
    normal = pygame.Color(128,128,128,128)
    over = pygame.Color(128,128,128,128)
    active = pygame.Color(128,128,128,128)
    
    normal.hsva = (hue, 50, 50, 100)
    over.hsva = (hue, 75, 50, 100)
    active.hsva = (hue, 75, 75, 100)

    return(normal, over, active)


pygame.init() #this may cause problems with sound

# setup the display... Resolution is ignored on Android
s = pygame.display.set_mode((640, 480))

r = s.get_rect()
surface = pygame.Surface(r.size)
surfrect = surface.get_rect()

clock = t.Clock() # for frame rate control


#function to change a parameter using a callback
def changeParam(vid, var):
    global damping, points,force
    new_val = 0
    if vid == 'damp':
        damping = damping * 10**(0.1*var[1]/surfrect.h)
        damping = max(0,min(damping, 1))
        new_val = damping
    elif vid == 'points':
        points = int(round(points * 2**(var[0]/surfrect.h)))
        points = max(4,min(points, 4096))
        new_val = points#(points, points * 2**(var[0]/surfrect.h))
        resampleWave(wave1,points)
        initWaveRender(wave1,points)
    elif vid == 'force':
        force = force * 10**(0.1*var[1]/surfrect.h)
        force = max(0,min(force, 2))
        new_val = force
    if timer('param_printer', rate=100):
        print(new_val, var)
        msg.showValue(vid, new_val)

#function to quite on button press
def action_quit(vid=None, var=None):
    pygame.quit()
    sys.exit()
    
def action_debug(vid=None, var=None):
    print(damping)
    
def action_toggle_sim(vid=None, var=None):
    global run_simulation
    run_simulation = not run_simulation
    
    
#auto coord system
#some control to activate the above callbacks
controls = []
controls.append(Control(surface, (0,surfrect.h-64),(64,64),getButtonColors(90),hd_act=changeParam,vid='points'))
controls.append(Control(surface, (0,0),(64,64),getButtonColors(0),img=imgs['exit'],up_act=action_quit,vid='exit'))
controls.append(Control(surface, (surfrect.w-64,0),(64,64),getButtonColors(180),img=imgs['update'],dn_act=action_toggle_sim,vid='pause'))
controls.append(Control(surface, (surfrect.w-64,surfrect.h-64),(64,64),getButtonColors(270),img=imgs['inforce'],hd_act=changeParam,vid='force'))






# initialise the sample points
initWaveRender(wave1, points)

#varibles for tracking selection of points
touched = False
touch_id = 0


run_simulation = True
#--------------------------- main loop
while True:
    #process wave mouseover effect
    if not touched:
        touch_id = -1
        for n in range(points):
            if wave1['rsel'][n].collidepoint(ms.get_pos()):
                touch_id = n
                if timer('touch_printer'):
                    print(touch_id, " - P:", wave1['pos'][n], "; V:", wave1['vel'][n], "; A:", wave1['acc'][n])
                break
                
    #process events
    for ev in pygame.event.get():
        #ceheck for quit signal
        if ev.type == QUIT:
            action_quit()
        else:
            #check for control activations
            con_act = False
            for con in controls:
                if con.processEvent(ev):
                    con_act = True
                    break
            #check for wave interaction
            if not con_act:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if touch_id >= 0:
                        touched = True
                        ms.get_rel()            
                elif ev.type == pygame.MOUSEBUTTONUP:
                    touched = False
    

    #frame rate limit
    clock.tick(60)
    
    # background
    surface.fill(pygame.Color(0, 0, 0))
 
    #update controls
    for con in controls:
        con.update()
        con.draw()
    
    #process wave sample manipulation
    if touched:
        pos = wave1['pos'][touch_id]
        vel = ms.get_rel()
        pos = pos+vel
        pos[0] = wave1['tar'][touch_id,0]
        wave1['pos'][touch_id] = pos
        wave1['vel'][touch_id][1] = lerp(vel[0], wave1['vel'][touch_id][1],0.5)
        wave1['vel'][touch_id][0] = 0
        #print("id:",touch_id," x:",pos[0]," y:",pos[1])

    if run_simulation:
        #calculate accelerations
        wave1['acc'].fill(0)
        wave1['tar'][:,1] = np.correlate(wave1['pos'][:,1], kernel2, mode='same')
        
        wave1['tar'][-1,1] = lerp(wave1['tar'][-1,1],0,end_damping[1])
        wave1['tar'][0,1] = lerp(wave1['tar'][-0,1],0,end_damping[0])
        '''
        for n in range(1,points):
            dd = (wave1['pos'][n-1] - wave1['pos'][n]) * force
    #        dd = np.sign(dd)*dd*dd
            dd[0] = 0;
            wave1['acc'][n] = wave1['acc'][n]+dd
            wave1['acc'][n-1] = wave1['acc'][n-1]-dd
        '''
        #process boundary conditions
        wave1['acc'] = wave1['acc']+(wave1['tar'] - wave1['pos']) * force# * wave1['mask']
            
        #integrate motion parameters
        wave1['vel'] = wave1['vel'] + wave1['acc']
        wave1['vel'] = wave1['vel'] * damping
        wave1['pos'] = wave1['pos'] + wave1['vel']
        wave1['pos'] = np.clip(wave1['pos'],-10000,10000)
    #calculate aux data
    aux_val = wave1['tar'][:,1]
    #draw wave elements
    for n in range(points):
        wr = wave1['rects'][n]
        wr.x = (surfrect.w*(wave1['pos'][n,0] ))
        wr.y = (surfrect.h*(0.5)+wave1['pos'][n,1])
        wr = wr.clip(surfrect)
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
        ar = ar.clip(surfrect)
        surface.fill((128,128,0), ar)
    
    #draw the buffer surface to the window surface
    surface.set_alpha(192)
    s.blit(surface, (0,0))
    
    sprint(s, msg.msg, msg.crd)
    pygame.display.flip()
