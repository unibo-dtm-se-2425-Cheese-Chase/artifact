from .vector import Vector2
from .constants import *
import numpy as np

class Cheese(object):
    def __init__(self, row, column, spritesheet=None):
        self.name = CHEESE
        self.position = Vector2(column*TILEWIDTH, row*TILEHEIGHT)
        self.collideRadius = 2 * TILEWIDTH / 16
        self.points = 10
        self.visible = True
        self.spritesheet = spritesheet
        self.image = spritesheet.getImage(8, 0)
        
    def render(self, screen):
        if self.visible:
            screen.blit(self.image, self.position.asTuple())

class PowerCheese(Cheese):
    def __init__(self, row, column, spritesheet):
        Cheese.__init__(self, row, column,spritesheet)
        self.name = POWERCHEESE
        self.points = 50
        self.flashTime = 0.4
        self.timer= 0
        self.image = spritesheet.getImage(10,0)
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.flashTime:
            self.visible = not self.visible
            self.timer = 0


class CheeseGroup(object):
    def __init__(self, cheesefile, spritesheet=None):
        self.cheeseList = []
        self.powercheeses = []
        self.spritesheet = spritesheet
        self.createCheeseList(cheesefile)
        self.numEaten = 0

    def update(self, dt):
        for powercheese in self.powercheeses:
            powercheese.update(dt)
                
    def createCheeseList(self, cheesefile):
        data = self.readCheesefile(cheesefile)        
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] in ['.', '+']:
                    self.cheeseList.append(Cheese(row, col, self.spritesheet))
                elif data[row][col] in ['P', 'p']:
                    pp = PowerCheese(row, col, self.spritesheet)
                    self.cheeseList.append(pp)
                    self.powercheeses.append(pp)
                    
    def readCheesefile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    def isEmpty(self):
        if len(self.cheeseList) == 0:
            return True
        return False
    
    def render(self, screen):
        for cheese in self.cheeseList:
            cheese.render(screen)