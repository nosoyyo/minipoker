# __author__ = arslan
# __date__ = 2021/10/11

import time
import random
from typing import List

from thpoker.core import Hand, Table, Combo, Cards
#from exceptions import *


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
            print(f'目前底池：{self.pools[0]}\n')


class Player():
    def __init__(self, cash, name=None, AI=True) -> None:
        if not name:
            name = 'arslan'
        self.name = name
        self.AI = AI
        self.hand = []
        self.cash = cash

    def __repr__(self) -> str:
        return f'<玩家：{self.name}>'

    def Draw(self):
        global DEBUG
        self.hand.append(RawCards.pop())
        self.hand.append(RawCards.pop())
        self.Combo()
        if DEBUG:
            print(f'{self.name}的手牌：{self.ShowHand()}\n')
    
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
    
    def ChooseOpponent(self):
        opponent = random.choice(PLAYERS)
        if opponent.name == self.name:
            opponent = self.ChooseOpponent()
        return opponent

    def Decide(self):
        global LASTBET

        print(f'{self.name}正在决策...')
        time.sleep(random.random()+2)

        # power = self.PowerCheck() #TODO
        power = int(random.random() * 100)
        if power < 20:
            self.Talk('fold')
        elif 20 <= power < 50:
            self.Talk('call')
            bet = LASTBET
        elif 50 <= power < 90:
            self.Talk('raise')
            bet  = SB * (int(random.random()*10) + 1)
            self.Bet(bet)
        elif power >= 90:
            self.Talk('allin')
            bet = self.Bet(self.cash)
        self.Bet(SB)


class Game():
    
    def __init__(self, n_AI=5, SB=5, cash=600):
        self.DEBUG = True
        self.TABLE = []
        self.PREFLOP_FLAG = False
        self.FLOP_FLAG = False
        self.TURN_FLAG = False
        self.RIVER_FLAG = False
        self.POOL = Pool()
        self.SB = SB
        self.BB = SB*2
        self.LASTBET = self.BB
        self.PLAYER = Player(cash=cash, AI=False)
        self.RawCards = self.Shuffle()

        self.MakeUpAI(n_AI, cash)
        self.PLAYERS = self.AI + [self.PLAYER]
        random.shuffle(self.PLAYERS)

        # init trash talk phase
        for p in self.PLAYERS:
            q = random.random()
            opponent = p.ChooseOpponent()
            if q > 0.7:
                p.Talk('trash',p=opponent)

    def MakeUpAI(self, n_AI, cash):
        '''
        0 - SB
        1 - BB
        2 - UTG
        3 - UTG + 1
        4 - CO
        5 - BT
        '''
        self.AI = []
        AI_NAMES = ['云师','jimmy仔','修师','范师','西米','铁锤','Zakk','胡哥','六爷','莎翁',]
        random.shuffle(AI_NAMES)
        result = AI_NAMES[:n_AI]
        result = list(map(lambda x: Player(name=x, cash=cash), result))
        random.shuffle(result)
        self.AI = result
    
    def Shuffle(self):
        num_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        suit_list = ['s', 'h', 'c', 'd']
        RawCards = [x + y for x in num_list for y in suit_list]

        # once is enough yeah true but
        random.shuffle(RawCards)
        random.shuffle(RawCards)
        random.shuffle(RawCards)
        return RawCards
    
    def Preflop(self):
        if not self.PREFLOP_FLAG:
            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Draw()
            self.PREFLOP_FLAG = True
            return
        else:
            print('already PREFLOP!')

    def Flop(self):
        if not self.FLOP_FLAG:
            self.TABLE.append(self.RawCards.pop())
            self.TABLE.append(self.RawCards.pop())
            self.TABLE.append(self.RawCards.pop())

            ShowHand(self.TABLE)

            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Combo()

            self.FLOP_FLAG = True

        else:
            raise AlreadyFlopError('already FLOP!!')
        print(f'current TABLE: {self.TABLE}\n')

    def Turn(self):

        if not self.TURN_FLAG:
            self.TABLE.append(self.RawCards.pop())

            ShowHand(self.TABLE)

            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Combo()
            
            self.TURN_FLAG = True

        else:
            raise AlreadyTurnError('already TURN!!')
        print(f'current TABLE: {self.TABLE}\n')

    def River(self):

        if not self.RIVER_FLAG:
            self.TABLE.append(self.RawCards.pop())

            ShowHand(self.TABLE)

            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Combo()

            self.RIVER_FLAG = True
            return self.TABLE
        else:
            raise AlreadyRiverError('already RIVER!!')
        print(f'current TABLE: {TABLE}\n')

def ShowHand(slashstring) -> Table:
    '''
    :slashstring: e.g. like '6d/As/Th' in TABLE
    '''
    string = ''
    for i in range(len(slashstring)):
        string += slashstring[i] + '/'
    return(Table(string[:-1]))


def main():

    game = Game()

    global POOL
    # check SB
    print()
    if game.PLAYERS[0].AI:
        POOL = game.PLAYERS[0].Bet(game.SB)
    else:   
        POOL = game.PLAYER.Bet(game.SB)

    # check BB
    if game.PLAYERS[1].AI:
        POOL = game.PLAYERS[1].Bet(game.SB*2)
    else:   
        POOL = game.PLAYER.Bet(game.SB*2)

    # Preflop
    game.Preflop()
    for i in range(2, 6):
        game.PLAYERS[i].Decide()
    print(f'你的手牌：{game.PLAYER.ShowHand()}\n',)

    # Flop
    game.Flop()
    for i in range(0, 6):
        game.PLAYERS[i].Decide()
    print(f'你的手牌：{game.PLAYER.ShowHand()}\n',)