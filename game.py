# __author__ = arslan
# __date__ = 2021/10/11

import random

from thpoker.core import Hand, Table, Combo, Cards
from exceptions import *


global DEBUG
DEBUG = False


class Player():
    def __init__(self, name=None, AI=True) -> None:
        if not name:
            name = 'arslan'
        self.name = name
        self.AI = AI
        self.hand = []
        self.cash = 600

    def __repr__(self) -> str:
        return f'<玩家：{self.name}>'

    def Draw(self):
        global DEBUG
        self.hand.append(RawCards.pop())
        self.hand.append(RawCards.pop())
        self.Combo()
        if DEBUG:
            self.ShowHand()
    
    def ShowHand(self):
        string = ''
        for i in range(len(self.hand)):
            string += self.hand[i] + '/'
        return(Hand(string))

    def Bet(self, bet, pool):
        if self.cash < bet:
            raise OverBetError(f'不能下这些，你只有{self.cash}了')
        else:
            self.cash -= bet
            pool += bet
        return pool

    def Talk(self):
        pass

    def Combo(self):
        global TABLE
        global DEBUG
        self.combo = Combo(hand=self.ShowHand(), table=ShowHand(TABLE))
        if DEBUG:
            print(self.combo)
        return self.combo


def MakeUpPlayers(num: int=5):
    '''
    :TODO: randomly decide who is SB/BB/...
    0 - SB
    1 - BB
    2 - UTG
    3 - UTG + 1
    4 - CO
    5 - BT
    '''
    global PLAYERS
    PLAYERS = {}
    AI_NAMES = ['云师','jimmy仔','修师','范师','西米','铁锤','Zakk','胡哥','六爷','莎翁',]
    random.shuffle(AI_NAMES)
    result = AI_NAMES[:num]
    result = list(map(lambda x: Player(name=x), result))
    result.append(PLAYER)
    random.shuffle(result)

    for i in range(num+1):
        PLAYERS.update({i:result[i]})

    return PLAYERS


def Shuffle():
    global RawCards
    num_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    suit_list = ['s', 'h', 'c', 'd']
    RawCards = [x + y for x in num_list for y in suit_list]
    # once is enough yeah but
    random.shuffle(RawCards)
    random.shuffle(RawCards)
    random.shuffle(RawCards)
    return RawCards


def ShowHand(slashstring):
    '''
    :slashstring: e.g. like '6d/As/Th' in TABLE
    '''
    string = ''
    for i in range(len(slashstring)):
        string += slashstring[i] + '/'
    return(Table(string[:-1]))


def InitGame():

    global TABLE
    TABLE = []

    global PREFLOP_FLAG
    PREFLOP_FLAG = False

    global FLOP_FLAG
    FLOP_FLAG = False

    global TURN_FLAG
    TURN_FLAG = False

    global RIVER_FLAG
    RIVER_FLAG = False

    global POOL
    POOL = 0

    global PLAYER
    PLAYER = Player(AI=False)

    global RawCards
    RawCards = Shuffle()

    MakeUpPlayers()


def Preflop():
    global PREFLOP_FLAG
    global PLAYERS
    if not PREFLOP_FLAG:
        for i in range(len(PLAYERS)):
            PLAYERS[i].Draw()
        PREFLOP_FLAG = True
        return
    else:
        print('already PREFLOP!')


def Flop():
    global FLOP_FLAG
    global TABLE
    if not FLOP_FLAG:
        TABLE.append(RawCards.pop())
        TABLE.append(RawCards.pop())
        TABLE.append(RawCards.pop())

        ShowHand(TABLE)

        for i in range(len(PLAYERS)):
            PLAYERS[i].Combo()

        FLOP_FLAG = True
        return TABLE
    else:
        raise AlreadyFlopError('already FLOP!!')
    print(f'current TABLE: {TABLE}')


def Turn():
    global TURN_FLAG
    global TABLE
    if not TURN_FLAG:
        TABLE.append(RawCards.pop())

        ShowHand(TABLE)

        for i in range(len(PLAYERS)):
            PLAYERS[i].Combo()
        
        TURN_FLAG = True
        return TABLE
    else:
        raise AlreadyTurnError('already TURN!!')
    print(f'current TABLE: {TABLE}')


def River():
    global RIVER_FLAG
    global TABLE
    if not RIVER_FLAG:
        TABLE.append(RawCards.pop())

        ShowHand(TABLE)

        for i in range(len(PLAYERS)):
            PLAYERS[i].Combo()

        RIVER_FLAG = True
        return TABLE
    else:
        raise AlreadyRiverError('already RIVER!!')
    print(f'current TABLE: {TABLE}')
