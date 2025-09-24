import pygame
from ..model.constants import *
import numpy as np
from .animation import Animator

BASETILEWIDTH = 16
BASETILEHEIGHT = 16
DEATH = 5

class Spritesheet(object):
    def __init__(self):
        self.sheet = pygame.image.load("CheeseChase/resources/spritesheet2.png").convert()
        transcolor = self.sheet.get_at((0,0))
        self.sheet.set_colorkey(transcolor)
        
    def getImage(self, x, y, width, height):
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())


class MouseSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)
        self.entity = entity
        self.entity.image = self.getStartImage()         
        self.animations = {}
        self.defineAnimations()
        self.stopimage = (0, 0)

    def defineAnimations(self):
        self.animations[DEATH] = Animator(((0, 6), (2, 6), (4, 6), (6, 6), (8, 6), (10, 6), (12, 6), (14, 6), (16, 6), (18, 6)), speed=6, loop=False)

    def update(self, dt):
        if self.entity.alive == True:
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(0,0)
                self.stopimage = (0, 0)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(2,0)
                self.stopimage = (2, 0)
            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(4,0)
                self.stopimage = (4,0)
            elif self.entity.direction == UP:
                self.entity.image = self.getImage(6,0)
                self.stopimage = (6,0)
            elif self.entity.direction == STOP:
                self.entity.image = self.getImage(*self.stopimage)
        else:
            self.entity.image = self.getImage(*self.animations[DEATH].update(dt))

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()

    def getStartImage(self):
        return self.getImage(0, 0)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)


class CatSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)
        self.entity = entity
        self.entity.image = self.getStartImage()
        self.stopimage = (0, 2)

    def update(self, dt):
        if self.entity.mode.current in [SCATTER, CHASE]:
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(0, 2)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(2, 2)
            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(4, 2)
            elif self.entity.direction == UP:
                self.entity.image = self.getImage(6, 2)
        elif self.entity.mode.current == FREIGHT:
            self.entity.image = self.getImage(8, 2)
        elif self.entity.mode.current == SPAWN:
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(0, 4)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(2, 4)
            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(4, 4)
            elif self.entity.direction == UP:
                self.entity.image = self.getImage(6, 4)
               
    def getStartImage(self):
        return self.getImage(0, 2)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

class LifeSprites(Spritesheet):
    def __init__(self, numlives):
        Spritesheet.__init__(self)
        self.resetLives(numlives)

    def removeImage(self):
        if len(self.images) > 0:
            self.images.pop(0)

    def resetLives(self, numlives):
        self.images = []
        for i in range(numlives):
            self.images.append(self.getImage(0,0))

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)


class MazeSprites(Spritesheet):
    def __init__(self, mazefile, rotfile):
        Spritesheet.__init__(self)
        self.data = self.readMazeFile(mazefile)
        self.rotdata = self.readMazeFile(rotfile)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, TILEWIDTH, TILEHEIGHT)

    def readMazeFile(self, mazefile):
        return np.loadtxt(mazefile, dtype='<U1')

    def constructBackground(self, background, y):
        for row in list(range(self.data.shape[0])):
            for col in list(range(self.data.shape[1])):
                if self.data[row][col].isdigit():
                    x = int(self.data[row][col]) + 12
                    sprite = self.getImage(x, y)
                    rotval = int(self.rotdata[row][col])
                    sprite = self.rotate(sprite, rotval)
                    background.blit(sprite, (col*TILEWIDTH, row*TILEHEIGHT))
                #elif self.data[row][col] == '=':
                #    sprite = self.getImage(10, 8)
                #   background.blit(sprite, (col*TILEWIDTH, row*TILEHEIGHT))

        return background

    def rotate(self, sprite, value):
        return pygame.transform.rotate(sprite, value*90)
