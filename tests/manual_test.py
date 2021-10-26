from thpoker.core import Hand, Combo, Table, Cards


# Test Cards/Combos etc

hands = []
hands.append(Hand('As/Ah'))
hands.append(Hand('Qs/Js'))
hands.append(Hand('3s/2h'))
hands.append(Hand('6s/6h'))
hands.append(Hand('As/2h'))
hands.append(Hand('Jh/Td'))

combos = []
combos.append(Combo(cards=Cards('As/Ks/Qs/Js/Ts')))
combos.append(Combo(cards=Cards('Ts/9s/8s/7s/6s')))
combos.append(Combo(cards=Cards('As/Ah/Ac/Ad/Ts')))
combos.append(Combo(cards=Cards('Qc/Qd/Qs/Js/Jh')))
combos.append(Combo(cards=Cards('Ts/7s/5s/3s/2s')))
combos.append(Combo(cards=Cards('9s/8h/7c/6s/5d')))
combos.append(Combo(cards=Cards('As/Ah/Ac/Js/Ts')))
combos.append(Combo(cards=Cards('Kc/Ks/Qs/Td/Ts')))
combos.append(Combo(cards=Cards('As/Ks/Qs/Tc/Ts')))
combos.append(Combo(cards=Cards('As/Ts/8h/6c/2d')))


# Test PowerCheck

def TestPowerCheck():
    from game import Game
    from player import Player

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
