# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 21:15:19 2018

@author: Washu
"""
import pygame
from pygame.locals import *
import pygame.font as fn
import string

imgs = {}
imgs['update'] = pygame.image.load("res/baseline_update_black_18dp.png")
imgs['exit'] = pygame.image.load("res/baseline_exit_to_app_black_18dp.png")
imgs['inforce'] = pygame.image.load("res/baseline_inward_horz_black_18dp.png")


fn.init()
font = fn.SysFont('Calibri',30)
    
valid_chars = (string.ascii_letters + string.digits + string.punctuation + ' ')

def renderChars(font):
    chars = {}
    for c in valid_chars:
        chars[c] = font.render(c, True, (192,192,192))
    return chars

chars = renderChars(font)

font_height = font.get_height()
def sprint(srf, msg, coord=(0,0)):
    coo = list(coord)
    sr = srf.get_rect()
    for c in msg:
        try:
            cx = chars[c]
            cr = cx.get_rect()
            next_x = coo[0] + cr.w
            if next_x > sr.w:
                coo[0] = coord(0)
                coo[1] = coo[1] + font_height
                if coo[1] > sr.h:
                    break;
            srf.blit(cx, coo)
            coo[0] = next_x
        except KeyError: #what to do if it's not in the list?
            if c == '\n':
                coo[0] = coord(0)
                coo[1] = coo[1] + font_height
                if coo[1] > sr.h:
                    break;
    return tuple(coo)