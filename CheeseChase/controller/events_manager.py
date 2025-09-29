import pygame
from pygame.locals import *
from ..model.constants import *
from .levels_manager import LevelManager

class EventsManager:
    def __init__(self, game_controller):
        self.gc = game_controller  
        self.level_manager = LevelManager(game_controller)

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.gc.mouse.alive:
                        self.gc.pause.setPause(playerPaused=True)
                        if not self.gc.pause.paused:
                            self.gc.textgroup.hideText()
                            self.gc.showEntities()
                        else:
                            self.gc.textgroup.showText(PAUSETXT)

    def checkCheeseEvents(self):
        cheese = self.gc.mouse.eatCheeses(self.gc.cheeses.cheeseList)
        if cheese:
            self.gc.cheeses.numEaten += 1
            self.gc.updateScore(cheese.points)
            if self.gc.cheeses.numEaten == 30:
                self.gc.cats.cat3.startNode.allowAccess(RIGHT, self.gc.cats.cat3)
            if self.gc.cheeses.numEaten == 70:
                self.gc.cats.cat4.startNode.allowAccess(LEFT, self.gc.cats.cat4)
            self.gc.cheeses.cheeseList.remove(cheese)
            if cheese.name == POWERCHEESE:
                self.gc.cats.startFreight()
            if self.gc.cheeses.isEmpty():
                self.gc.flashBG = True
                self.gc.hideEntities()
                self.gc.pause.setPause(pauseTime=3, func=self.gc.level_manager.nextLevel)

    def checkCatEvents(self):
        for cat in self.gc.cats:
            if self.gc.mouse.collideCat(cat):
                if cat.mode.current is FREIGHT:
                    self.gc.mouse.visible = False
                    cat.visible = False
                    self.gc.updateScore(cat.points)
                    self.gc.textgroup.addText(str(cat.points), RED, cat.position.x, cat.position.y, 8, time=1)
                    self.gc.cats.updatePoints()
                    self.gc.pause.setPause(pauseTime=1, func=self.gc.showEntities)
                    cat.startSpawn()
                    self.gc.nodes.allowHomeAccess(cat)
                elif cat.mode.current is not SPAWN:
                    if self.gc.mouse.alive:
                        self.gc.lives -= 1
                        self.gc.lifesprites.removeImage()
                        self.gc.mouse.die()
                        self.gc.cats.hide()
                        if self.gc.lives <= 0:
                            self.gc.textgroup.showText(GAMEOVERTXT)
                            self.gc.pause.setPause(pauseTime=3, func=self.gc.level_manager.restartGame)
                        else:
                            self.gc.pause.setPause(pauseTime=3, func=self.gc.level_manager.resetLevel)

