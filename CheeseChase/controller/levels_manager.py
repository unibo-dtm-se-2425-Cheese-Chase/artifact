from pygame.locals import *
from ..model.constants import *

class LevelManager:
    def __init__(self, game_controller):
        self.gc = game_controller
        self.resetGameState()

    def resetGameState(self):
        self.gc.lives = 5
        self.gc.level = 0
        self.gc.score = 0
        self.gc.lifesprites.resetLives(self.gc.lives)
        self.gc.textgroup.updateScore(self.gc.score)
        self.gc.textgroup.updateLevel(self.gc.level)

    def resetEntities(self):
        self.gc.mouse.reset()
        self.gc.cats.reset()

    def nextLevel(self):
        self.gc.showEntities()
        self.gc.level += 1
        self.gc.pause.paused = True
        self.gc.startGame()
        self.gc.textgroup.updateLevel(self.gc.level)

    def restartGame(self):
        self.gc.pause.paused = True
        self.resetGameState()
        self.gc.startGame()
        self.gc.textgroup.showText(READYTXT)

    def resetLevel(self):
        self.gc.pause.paused = True
        self.resetEntities()
        self.gc.textgroup.showText(READYTXT)
