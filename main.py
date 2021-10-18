import random
import logging

from game import Game


logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s@%(name)s.%(funcName)s:\n%(message)s')
sh = logging.StreamHandler()
fh = logging.FileHandler('main.log')
sh.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(sh)
logger.addHandler(fh)


def main():

    game = Game()
    game.NewGame()
