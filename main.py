__VERSION__ = '-0.01α'

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
