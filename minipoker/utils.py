import time 
import random
from thpoker.core import Table


def ShowHand(slashstring) -> Table:
    '''
    :slashstring: e.g. like '6d/As/Th' in TABLE
    '''
    string = ''
    for i in range(len(slashstring)):
        string += slashstring[i] + '/'
    return(Table(string[:-1]))


def SortCombo(combos: list) -> list:
    '''
    :return: player index in game.PLAYERS
    '''
    n = len(combos)
    for i in range(n):
        for j in range(0, n-i-1):
            if combos[j] > combos[j+1]:
                combos[j], combos[j+1] = combos[j+1], combos[j]
    return combos

def GetSeed():
    import random
    _seed = 0
    levels = int(random.random().__str__()[-3:])
    for i in range(levels):
        random.seed(_seed)
        _seed += random.random()
    _seed = int(_seed.real.__str__()[-8:])
    return _seed
