import logging

from game import Game, Pool


logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s@%(name)s.%(funcName)s: %(message)s')
sh  = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)


def main():

    game = Game()

    def NewGame():
        game.OVER = False

        game.TABLE = []
        game.RawCards = game.Shuffle()
        game.POOL = Pool()
        game.Rotate(game.PLAYERS)
        game.TrashTalk()

        game.LASTBET = game.BB
        game.STAGE = 0
        game.WINNER = None

        # Preflop
        game.Preflop()

        for p in game.PLAYERS:
            if p.is_SB:
                game.POOL = p.Bet(game.SB, game)
            elif p.is_BB:
                game.POOL = p.Bet(game.BB, game)
            else:
                p.Decide(game)

        if game.OVER:
            NewGame()

        # Flop
        game.Flop()
        for p in game.PLAYERS:
            p.Decide(game)
        if game.OVER:
            NewGame()
        
        # Turn
        game.Turn()
        for p in game.PLAYERS:
            p.Decide(game)
        if game.OVER:
            NewGame()

        # River
        game.River()
        for p in game.PLAYERS:
            p.Decide(game)
        if game.OVER:
            NewGame()

    NewGame()