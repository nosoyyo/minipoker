import logging

from game import Game


def main():

    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh  = logging.StreamHandler(stream=None)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    game = Game()

    # Preflop
    game.Preflop()

    for p in game.PLAYERS:
        if p.is_SB:
            game.POOL = p.Bet(game.SB, game)
        elif p.is_BB:
            game.POOL = p.Bet(game.BB, game)
        else:
            p.Decide(game)

    # Flop
    game.Flop()
    for p in game.PLAYERS:
        p.Decide(game)
    
    # Turn
    game.Turn()
    for p in game.PLAYERS:
        p.Decide(game)

    # River
    game.River()
    for p in game.PLAYERS:
        p.Decide(game)