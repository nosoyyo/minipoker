import random
import logging
from rich.logging import RichHandler
from rich.traceback import install
install(show_locals=True)
from rich.live import Live

from game import Game

logging.basicConfig(
    level="INFO",
    format="'[%(levelname)s] %(asctime)s@%(name)s.%(funcName)s:\n%(message)s'",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)


#FORMAT = logging.Formatter('[%(levelname)s] %(asctime)s@%(name)s.%(funcName)s:\n%(message)s')
logger = logging.getLogger('main')
sh = logging.StreamHandler()
fh = logging.FileHandler('main.log')
rh = RichHandler()
#sh.setFormatter(FORMAT)
#fh.setFormatter(FORMAT)
logger.addHandler(sh)
logger.addHandler(fh)


def main():
        #with Live(game, refresh_per_second=4, screen=True):

        game = Game()
        game.NewGame()
