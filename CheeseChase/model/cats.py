from pygame.locals import *
from .vector import Vector2
from .constants import *
from .entity import Entity
from .modes import ModeController
from ..view.sprites import CatSprites

class Cat(Entity):
    def __init__(self, node, mouse=None, name = CAT):
        Entity.__init__(self, node)
        self.name = name
        self.points = 200
        self.goal = Vector2()
        self.directionMethod = self.goalDirection
        self.mouse = mouse
        self.mode = ModeController(self)
        self.homeNode = node
        self.sprites = CatSprites(self)

    def reset(self):
        Entity.reset(self)
        self.points = 200
        self.directionMethod = self.goalDirection

    def update(self, dt):
        self.sprites.update(dt)
        self.mode.update(dt)
        if self.mode.current is SCATTER:
            self.scatter()
        elif self.mode.current is CHASE:
            self.chase()
        Entity.update(self, dt)

    def scatter(self):
        self.goal = Vector2()

    def chase(self):
        self.goal = self.mouse.position

    def spawn(self):
        self.goal = self.spawnNode.position

    def setSpawnNode(self, node):
        self.spawnNode = node

    def startSpawn(self):
        self.mode.setSpawnMode()
        if self.mode.current == SPAWN:
            self.setSpeed(150)
            self.directionMethod = self.goalDirection
            self.spawn()

    def startFreight(self):
        self.mode.setFreightMode()
        if self.mode.current == FREIGHT:
            self.setSpeed(50)
            self.directionMethod = self.randomDirection         

    def normalMode(self):
        self.setSpeed(100)
        self.directionMethod = self.goalDirection
        self.homeNode.denyAccess(DOWN, self)
 
class CatGroup(object):
    def __init__(self, node, mouse):
        self.cat1 = Cat(node, mouse, name = CAT1)
        self.cat2 = Cat(node, mouse, name = CAT2)
        self.cat3 = Cat(node, mouse, name = CAT3)
        self.cat4 = Cat(node, mouse, name = CAT4)
        self.cats = [self.cat1, self.cat2, self.cat3, self.cat4]

    def __iter__(self):
        return iter(self.cats)

    def update(self, dt):
        for cat in self:
            cat.update(dt)

    def startFreight(self):
        for cat in self:
            cat.startFreight()
        self.resetPoints()

    def setSpawnNode(self, node):
        for cat in self:
            cat.setSpawnNode(node)

    def updatePoints(self):
        for cat in self:
            cat.points *= 2

    def resetPoints(self):
        for cat in self:
            cat.points = 200

    def hide(self):
        for cat in self:
            cat.visible = False

    def show(self):
        for cat in self:
            cat.visible = True

    def reset(self):
        for cat in self:
            cat.reset()

    def render(self, screen):
        for cat in self:
            cat.render(screen)

