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
                while not game.OVER:
                    game.CheckState()
                    p.Decide(game)
                else:
                    NewGame()

        # Preflop
        game.Preflop()

        for p in game.PLAYERS:
            if p.is_SB:
                game.POOL = p.Bet(game.SB, game)
            elif p.is_BB:
                game.POOL = p.Bet(game.BB, game)
            else:
                p.Decide(game)
        for p in game.PLAYERS[:2]:
            p.Decide(game, 'callOrFold')

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