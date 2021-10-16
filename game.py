# __author__ = arslan
# __date__ = 2021/10/11

import random
import logging

from exceptions import *
from player import Player
from utils import CORPUS, AI_NAMES, ShowHand, SortCombo


#ISSUE still actions after win
#TODO the 1st player of flop round should be able to check
#TODO CLI menu: 1/3 pool etc. helper
#TODO check winner and allocate money
#TODO improve Pool
#TODO BB needs to call or fold when someone allin at preflop stage
#TODO manual/auto SB raise
#ISSUE weird missing action of human player
#TODO side pool regularization
#TODO new game: SB/BB rotation
#TODO BB preflop raise
#TODO drawing calculation and related stuff(bluffing etc.)
#TODO real powercheck & probability helper
#TODO stuff about nuts: powercheck & talk
#TODO real AI: characteristics
#TODO random smalltalk
#TODO game history & stats
#TODO player/AI interact: trashtalk etc.
#TODO unit tests
#TODO UI
#TODO go online
#TODO web UI


class Pool:

    def __init__(self) -> None:
        self.pools = [0]
    
    def __len__(self) -> int:
        return len(self.pools)

    def Add(self, name: str, bet: int, index=0) -> None:
        self.pools[index] += bet
        self.ShowPool(name, bet)

    def Give(self, p, index=0):
        p.cash += self.pools[index]
        print(f'{p.name}赢了全部底池：${self.pools[index]}')
        self.pools[index] = 0

    def Side(self, bet: int, index)-> None:
        #TODO
        pass

    def ShowPool(self, name, bet)-> None:
        print(f'{name}下注{bet}')
        if len(self.pools) == 1:
            print(f'目前底池：{self.pools[0]}')
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
        self.TrashTalk()

        # distribue SB and BB
        self.Rotate(self.PLAYERS)

        # :0: init
        # :1: preflop
        # :2: flop
        # :3: turn
        # :4: river
        self.STAGE = 0

        self.LASTBET = self.BB
        self.WINNER = None
        self.OVER = False

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

    def TrashTalk(self):
        for p in self.PLAYERS:
            q = random.random()
            opponent = p.ChooseOpponent(self)
            if q > 0.7:
                p.Talk(self, 'trash', p=opponent)

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
            self.Allocate()
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
            self.Allocate()
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
            self.Allocate()

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
            self.Allocate()
        else:
            self.logger.error(f'game.STAGE should be 3, now {self.STAGE}!')
            raise GameStageError()

        print(f'current TABLE: {self.TABLE}\n')

    def Allocate(self):
        '''
        check winner and allocate money
        '''
        if len(self.PLAYERS) == 1:
            if len(self.POOL) == 1:
                winner = self.PLAYERS[0]
                self.POOL.Give(winner)
                self.OVER = True
            else:
                #TODO side-pool situations
                pass
                self.OVER = True
        elif self.STAGE == 4:
            if len(self.POOL) == 1:
                combos = [p.combo for p in self.PLAYERS]
                combos = SortCombo(combos)
                winner = ''
                for p in self.PLAYERS:
                    if p.combo == combos[-1]:
                        winner = p
                self.POOL.Give(winner)
                self.OVER = True
            else:
                #TODO side-pool situations
                pass
                self.OVER = True

    def Rotate(self):
        r = self.PLAYERS.pop(0)
        self.PLAYERS.append(r)

        for i in range(len(self.PLAYERS)):
            if i == 0:
                self.PLAYERS[i].is_SB = True
                self.PLAYERS[i].is_BB = False
            elif i == 1:
                self.PLAYERS[i].is_SB = False
                self.PLAYERS[i].is_BB = True
            else:
                self.PLAYERS[i].is_SB = False
                self.PLAYERS[i].is_BB = False
                
