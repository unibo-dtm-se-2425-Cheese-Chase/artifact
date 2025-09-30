import pygame
from pygame.locals import *
from ..model.constants import *

class GameView:
    def __init__(self, controller):
        self.controller = controller 

    def render(self):
        screen = self.controller.screen
        screen.blit(self.controller.background, (0, 0))
        self.controller.cheeses.render(screen)
        self.controller.mouse.render(screen)
        self.controller.cats.render(screen)
        self.controller.textgroup.render(screen)

        for i, img in enumerate(self.controller.lifesprites.images):
            x = img.get_width() * i
            y = SCREENHEIGHT - img.get_height()
            screen.blit(img, (x, y))
            
        pygame.display.update()

    