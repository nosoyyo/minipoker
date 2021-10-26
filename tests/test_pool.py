from thpoker.core import Hand, Combo, Table, Cards

from minipoker.player import Player
from minipoker.tests import MockGame


def test_pool_sum():
    game = MockGame()
    game._init_game()
    game._init_table()

    for p in game.PLAYERS:
        p.Bet(100)
    assert game.POOL.SUM == 600

    # mock game.NewRound()
    game._stage = 2

    game.PLAYERS[0].Fold()
    for p in game.PLAYERS:
        p.Bet(100)
    assert game.POOL.SUM == 1100

    # mock game.NewRound()
    game._stage = 3

    game.PLAYERS[0].AllIn()
    assert game.POOL.SUM == 1500

    game.OVER = True
    assert game.CheckState()
    game.WINNERS = [game.PLAYERS[0]]
    game._raw_table = ['Ad/Ac/Ts/Th/Kc']
    game.WINNERS[0]._raw_hand = ['As/Ah']
    game.POOL.Account()
    game.Summary()