from rich import print
from thpoker.core import Hand, Combo, Table, Cards

from minipoker.player import Player
from minipoker import MockGame
from minipoker.pool import Pool


def test_pool_sum():
    game = MockGame()
    game._init_game()
    game._init_table()
    game.POOL = Pool(game)
    print(game.POOL.pools)

    for p in game.PLAYERS:
        p.Bet(100)
    assert game.POOL.SUM == 600
    print(game.POOL.pools)

    # mock game.NewRound()
    game._stage = 2

    game.PLAYERS[0].Fold()
    for p in game.PLAYERS:
        p.Bet(100)
    assert game.POOL.SUM == 1100
    game.POOL.Account()
    print(game.POOL.pools)

    # mock game.NewRound()
    game._stage = 3

    game.PLAYERS[0].AllIn()
    assert game.POOL.SUM == 1500
    game.POOL.Account()
    print(game.POOL.pools)

    game.OVER = True
    assert game.CheckState()
    game.WINNERS = [game.PLAYERS[0]]
    game._raw_table = ['Ad/Ac/Ts/Th/Kc']
    game.WINNERS[0]._raw_hand = ['As/Ah']
    game.POOL.Account()
    game.Summary(debug=True)