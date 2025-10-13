import pygame
from pygame.locals import *
from sklearn import base
from ..model.constants import *
from ..model.mouse import Mouse
from ..model.nodes import NodeGroup
from ..model.cheeses import CheeseGroup
from ..model.cats import CatGroup
from .pauser import Pause
from ..view.text import TextGroup
from ..view.sprites import LifeSprites
from ..view.sprites import MazeSprites
from ..model.mazedata import MazeData
from .events_manager import EventsManager
from .levels_manager import LevelManager
from ..view.game_view import GameView 
from importlib import resources

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.mazedata = MazeData()
        self.events_manager = EventsManager(self)
        self.level_manager = LevelManager(self)
        self.view = GameView(self)

    def startGame(self):      
        self.mazedata.loadMaze(self.level)
        base = resources.files("CheeseChase.resources")
        maze_txt = base / f"{self.mazedata.obj.name}.txt"
        rotation_txt = base / f"{self.mazedata.obj.name}_rotation.txt"
        self.mazesprites = MazeSprites(str(maze_txt), str(rotation_txt))
        self.setBackground()
        self.nodes = NodeGroup(str(maze_txt))
        
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        
        self.mouse = Mouse(self.nodes.getNodeFromTiles(*self.mazedata.obj.mouseStart))
        self.cheeses = CheeseGroup(str(maze_txt), self.mazesprites)
        
        self.cats = CatGroup(self.nodes.getStartTempNode(), self.mouse)

        self.cats.cat2.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.cats.cat3.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.cats.cat4.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.cats.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.cats.cat1.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))

        self.nodes.denyHomeAccess(self.mouse)
        self.nodes.denyHomeAccessList(self.cats)
        self.cats.cat3.startNode.denyAccess(RIGHT, self.cats.cat3)
        self.cats.cat4.startNode.denyAccess(LEFT, self.cats.cat4)
        self.mazedata.obj.denyCatsAccess(self.cats, self.nodes)

    def setBackground(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(WHITE)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(WHITE)
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, self.level%5)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.cheeses.update(dt)
        if not self.pause.paused:
            self.cats.update(dt)      
            self.events_manager.checkCheeseEvents()
            self.events_manager.checkCatEvents()

        if self.mouse.alive:
            if not self.pause.paused:
                self.mouse.update(dt)
        else:
            self.mouse.update(dt)

        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.events_manager.checkEvents() 
        self.view.render()

    def showEntities(self):
        self.mouse.visible = True
        self.cats.show()

    def hideEntities(self):
        self.mouse.visible = False
        self.cats.hide()

    def updateScore(self, points):
       self.score += points
       self.textgroup.updateScore(self.score)

