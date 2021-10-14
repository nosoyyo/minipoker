# __author__ = arslan
# __date__ = 2021/10/11

import time
import random
from typing import List

from thpoker.core import Hand, Table, Combo, Cards
#from exceptions import *
#from utils import DEBUG, Shuffle, CORPUS



class Pool:

    def __init__(self) -> None:
        self.pools = [0]

    def Add(self, name: str, bet: int, index=0)-> None:
        self.pools[index] += bet
        self.ShowPool(name, bet)

    def Side(self, bet: int, index)-> None:
        pass

    def ShowPool(self, name, bet)-> None:
        print(f'{name}下注{bet}')
        if len(self.pools) == 1:
            print(f'目前底池：{self.pools[0]}')


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
            print(f'{self.name}的手牌：{self.ShowHand()}')
    
    def ShowHand(self) -> Hand:
        string = ''
        for i in range(len(self.hand)):
            string += self.hand[i] + '/'
        return(Hand(string))

    def Bet(self, bet) -> Pool:
        if self.cash < bet:
            raise OverBetError(f'不能下这些，你只有{self.cash}了')
        else:
            self.cash -= bet
            POOL.Add(self.name, bet)
        return POOL

    def Talk(self, command, p=None):
        time.sleep(1)
        if command == 'fold':
            word = random.choice(CORPUS['FOLD'])            
        elif command == 'check':
            word = random.choice(CORPUS['CHECK'])
        elif command == 'call':
            word = random.choice(CORPUS['CALL'])
        elif command == 'raise':
            word = random.choice(CORPUS['RAISE'])
        elif command == 'allin':
            word = random.choice(CORPUS['ALLIN'])
        elif command == 'trash':
            trash = random.choice(CORPUS['TRASHTALK'])
            word = f'{trash}{p.name}'
        print(f'{self.name}：{word}')

    def Combo(self) -> Combo:
        global TABLE
        global DEBUG
        self.combo = Combo(hand=self.ShowHand(), table=ShowHand(TABLE))
        if DEBUG:
            print(f'{self.name}的combo：{self.combo}')
        return self.combo

    def PowerCheck(self):
        # flush check
        # ace check
        return 50
    
    def Decide(self):
        time.sleep(random.random()+2)
        if DEBUG:
            print(f'{self.name}正在决策...')
        # power = self.PowerCheck() #TODO
        power = int(random.random() * 100)
        if power < 20:
            self.Talk('fold')
        elif 20 <= power < 50:
            self.Talk('call')
            self.Bet(SB)
        elif 50 <= power < 90:
            self.Talk('raise')
            bet  = SB * (int(random.random()*10) + 1)
            self.Bet(bet)
        elif power >= 90:
            self.Talk('allin')
            bet = self.Bet(self.cash)


def ChooseOpponent(p):
    opponent = random.choice(PLAYERS)
    if opponent.name == p.name:
        opponent = ChooseOpponent(p)
    return opponent

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
    PLAYERS = []
    AI_NAMES = ['云师','jimmy仔','修师','范师','西米','铁锤','Zakk','胡哥','六爷','莎翁',]
    random.shuffle(AI_NAMES)
    result = AI_NAMES[:num]
    result = list(map(lambda x: Player(name=x), result))
    result.append(PLAYER)
    random.shuffle(result)
    PLAYERS = result

    # init trash talk phase
    for p in PLAYERS:
        q = random.random()
        opponent = ChooseOpponent(p)
        if q > 0.7:
            p.Talk('trash',p=opponent)

    return PLAYERS


def ShowHand(slashstring) -> Table:
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
    POOL = Pool()

    global SB
    SB = 5

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


def main():
    InitGame()

    global POOL
    # check SB
    print()
    if PLAYERS[0].AI:
        POOL = PLAYERS[0].Bet(SB)
    else:   
        POOL = PLAYER.Bet(SB)

    # check BB
    if PLAYERS[1].AI:
        POOL = PLAYERS[1].Bet(SB*2)
    else:   
        POOL = PLAYER.Bet(SB*2)

    # Preflop
    Preflop()
    for i in range(2, 6):
        PLAYERS[i].Decide()
    print(f'你的手牌：{PLAYER.ShowHand()}',)

    # Flop
    Flop()
    for i in range(0, 6):
        PLAYERS[i].Decide()
    print(f'你的手牌：{PLAYER.ShowHand()}',)