import logging
from pygame.locals import *
from .controller.game_controller import GameController

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('CheeseChase')

__all__ = ["GameController"]

# let this be the last line of this file
logger.info("CheeseChase loaded")