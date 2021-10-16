import random
import logging

from game import Game, Pool


logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%levelname] %(asctime)s@%(name)s.%(funcName)s:\n%(message)s')
sh = logging.StreamHandler()
fh = logging.FileHandler('main.log')
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.addHandler(fh)


def main():

    game = Game()

    def NewGame():
        game.OVER = False
        game.NUMOFGAMES += 1

        game.TABLE = []
        game.RawCards = game.Shuffle()
        game.POOL = Pool()
        game.Rotate()
        logger.info(f'{game.PLAYERS[0]}小盲')
        logger.info(f'{game.PLAYERS[1]}大盲')
        game.TrashTalk()

        game.LASTBET = game.BB
        game.STAGE = 0
        game.WINNER = None

        def Action():
            for p in game.PLAYERS:
                over = game.CheckState()
                if over:
                    NewGame()
                else:
                    p.Decide(game)

        # Preflop
        game.Preflop()

        game.SBPLAYER.Bet(game.SB, game)
        game.BBPLAYER.Bet(game.BB, game)

        for p in game.PLAYERS[2:]:
            p.Decide(game)

        for p in game.PLAYERS[:2]:
            p.Decide(game)

        # Flop
        game.Flop()
        Action()
        
        # Turn
        game.Turn()
        Action()

        # River
        game.River()
        Action()

    NewGame()