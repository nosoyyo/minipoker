__AUTHOR__ = "arslan"
__EMAIL__ = "oyyoson@gmail.com"
__COPYRIGHT__ = "Copyright © 2021 MSFC Studios. All rights reserved."
__LICENSE__ = "MIT"
__VERSION_INFO__ = (0, 0, -1, 'α')
__VERSION__ = ".".join(map(str, __VERSION_INFO__))

import random
import logging
from rich.traceback import install
install(show_locals=True)
from rich.logging import RichHandler

from game import Game

logging.basicConfig(
    level="WARNING",
    format="'[%(levelname)s] %(asctime)s@%(name)s.%(funcName)s:\n%(message)s'",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)


#FORMAT = logging.Formatter('[%(levelname)s] %(asctime)s@%(name)s.%(funcName)s:\n%(message)s')
logger = logging.getLogger('main')
#rh = RichHandler()
#sh = logging.StreamHandler()
#sh.setFormatter(FORMAT)
#logger.addHandler(sh)
#fh.setFormatter(FORMAT)
fh = logging.FileHandler('main.log')
logger.addHandler(fh)


def main():
        #with Live(game, refresh_per_second=4, screen=True):

        game = Game()
        game.NewGame()
