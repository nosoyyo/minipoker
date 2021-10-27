from minipoker.player import Player
from .mock import MockGame

def test_Player():
    game = MockGame()
    from minipoker.player import Player
    p = Player(game, is_AI=False)


# Test PowerCheck

def test_PowerCheck():
    from minipoker.game import Game
    from minipoker.player import Player

    game = Game()
    game.Shuffle()
    p = Player(game)
    game.CARDSDEALT = []
    game._stage = 1
    p._raw_hand.append(game.Deal())
    p._raw_hand.append(game.Deal())
    self = p
    p.PowerCheck()
    print(f'p.HAND {p.HAND}\n p._power {p._power}')
