# __author__ = arslan
# __date__ = 2021/10/11

import random
import logging

from thpoker.core import Hand, Table, Combo, Cards

from exceptions import *
from player import Player
from utils import CORPUS, AI_NAMES, ShowHand


#TODO BB needs to call or fold when someone allin at preflop stage
#TODO CLI menu: 1/3 pool etc. helper
#TODO winner decide 
#TODO manual/auto SB raise
#TODO side pool regularization
#TODO new game: SB/BB rotation
#TODO BB preflop raise
#TODO drawing calculation and related stuff(bluffing etc.)
#TODO real powercheck
#TODO stuff about nuts: powercheck & talk
#TODO real AI
#TODO random smalltalk
#TODO player/AI interact: trashtalk etc.
#TODO unit tests
#TODO UI
#TODO go online
#TODO web UI


class Pool:

    def __init__(self) -> None:
        self.pools = [0]

    def Add(self, name: str, bet: int, index=0)-> None:
        self.pools[index] += bet
        self.ShowPool(name, bet)

    def Side(self, bet: int, index)-> None:
        #TODO
        pass

    def ShowPool(self, name, bet)-> None:
        print(f'{name}下注{bet}')
        if len(self.pools) == 1:
            print(f'目前底池：{self.pools[0]}\n')
        else:
            #TODO
            pass


class Game():
    
    def __init__(self, n_AI=5, SB=5, cash=600):
        self.logger = logging.getLogger('main.game')

        self.TABLE = []
        self.RawCards = self.Shuffle()
        self.POOL = Pool()
        self.SB = SB
        self.BB = SB*2

        self.PLAYER = Player(cash=cash, is_AI=False)
        self.MakeUpAI(n_AI, cash)
        self.PLAYERS = self.AI + [self.PLAYER]
        random.shuffle(self.PLAYERS)

        # distribute positions
        self.PLAYERS[0].is_SB = True
        self.PLAYERS[1].is_BB = True

        # init trash talk phase
        for p in self.PLAYERS:
            q = random.random()
            opponent = p.ChooseOpponent(self)
            if q > 0.7:
                p.Talk(self, 'trash', p=opponent)
        self.LASTBET = self.BB
        self.CHECKED = False

        # :0: init
        # :1: preflop
        # :2: flop
        # :3: turn
        # :4: river
        self.STAGE = 0

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

    def Deal(self, player):
        card1 = self.RawCards.pop()
        card2 = self.RawCards.pop()
        self.logger.debug(f'给{player.name}发了一张{card1}')
        self.logger.debug(f'给{player.name}发了一张{card2}\n')
        player.hand.append(card1)
        player.hand.append(card2)
 
    def Preflop(self):
        print('\nPreflop阶段\n')
        if self.STAGE == 0:
            for i in range(len(self.PLAYERS)):
                self.Deal(self.PLAYERS[i])
            self.STAGE = 1
            return
        else:
            self.logger.error(f'game.STAGE should be 0, now {self.STAGE}!')
            raise GameStageError()

    def Flop(self):
        print('\nFlop阶段\n')
        if self.STAGE == 1:
            self.TABLE.append(self.RawCards.pop())
            self.TABLE.append(self.RawCards.pop())
            self.TABLE.append(self.RawCards.pop())
            ShowHand(self.TABLE)
            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Combo(self)
            self.STAGE = 2
        else:
            self.logger.error(f'game.STAGE should be 1, now {self.STAGE}!')
            raise GameStageError()
        print(f'current TABLE: {self.TABLE}\n')

    def Turn(self):
        print('\n转牌圈\n')

        if self.STAGE == 2:
            self.TABLE.append(self.RawCards.pop())
            ShowHand(self.TABLE)
            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Combo(self)          
            self.STAGE = 3

        else:
            self.logger.error(f'game.STAGE should be 2, now {self.STAGE}!')
            raise GameStageError()
        print(f'current TABLE: {self.TABLE}\n')

    def River(self):
        print('\n河牌圈\n')

        if self.STAGE == 3:
            self.TABLE.append(self.RawCards.pop())
            ShowHand(self.TABLE)
            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Combo(self)
            self.STAGE = 4
        else:
            self.logger.error(f'game.STAGE should be 3, now {self.STAGE}!')
            raise GameStageError()

        print(f'current TABLE: {self.TABLE}\n')

