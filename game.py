# __author__ = arslan
# __date__ = 2021/10/11

import sys
import random
import logging
from typing import List
from thpoker.core import Table

from exceptions import *
from player import Player
from utils import CORPUS, AI_NAMES, SortCombo


class Pool:

    def __init__(self, n_players) -> None:
        self.pools = [[0]]
        self.pools = [[i for i in self.pools[0] for j in range(n_players)]]
    
    def __len__(self) -> int:
        return len(self.pools)
    
    def __repr__(self) -> str:
        #TODO
        return str(sum(self.pools[0]))

    def Add(self, p: Player, bet: int, index=0) -> None:
        self.pools[index][p.INDEX] += bet
        self.ShowPool(p, bet)

    def Give(self, p, index=0) -> None:
        p.CASH += sum(self.pools[index])
        print(f'{p.NAME}以{p.COMBO}赢得全部底池：${sum(self.pools[index])}')
        # here we do no clean, will do Pool.__init__ later in NewGame()

    def Side(self, bet: int, index) -> None:
        #TODO
        pass

    def ShowPool(self, p: Player, bet) -> None:
        print(f'{p.NAME}下注 ${bet}，剩余现金 ${p.CASH}')
        if len(self.pools) == 1:
            print(f'目前底池 ${sum(self.pools[0])}')
        else:
            #TODO
            pass


class Positions():

    def __init__(self, n=6):
        self.SB = None
        self.BB = None
        self.UTG = None
        self.UTG1 = None
        self.CO = None
        self.BTN = None

    def __len__(self):
        return len(list(self.__dict__.keys()))

    def Add(self, p):
        if self.AVAILABLE:
            key = random.choice(list(self.__dict__.keys()))
            self.__dict__[key] = p
        else:
            raise GameAlreadyFullError()

    @property
    def AVAILABLE(self):
        flag = True
        if all(self.__dict__.values()):
            flag = False
        return flag


class Game():
    
    def __init__(self, n_AI=5, SB=5, buyin=600) -> None:
        self.logger = logging.getLogger('main.self')

        self.POSITIONS = Positions(n_AI)
        self.BUYIN = buyin
        self.NUMOFGAMES = 0
        self._raw_table = []
        self.RAWCARDS = self.Shuffle()
        self.SB = SB
        self.BB = SB*2

        self.PLAYER = Player(self, is_AI=False)

    def NewGame(self) -> None:

        self.NUMOFGAMES += 1
        print(f'\n第{self.NUMOFGAMES}局')
        self.OVER = False
        
        if self.NUMOFGAMES == 1:
            for i in range(len(self.POSITIONS)-1):
                self.WORLD.pop().BuyIn()
            self.PLAYER.BuyIn()
        else:
            if self.POSITIONS.AVAILABLE:
                self.WORLD.pop().BuyIn()

        # distribute SB/BB
        self.Rotate()
        self.logger.info(f'{self.PLAYERS[0]} 小盲')
        self.logger.info(f'{self.PLAYERS[1]} 大盲')

        self.TrashTalk()

        self.LASTBET = self.BB
        self.WINNER = None

        for p in self.PLAYERS:
            p._raw_hand = []  
        self._raw_table = []
        self.RAWCARDS = self.Shuffle()

        # init or re-init POOL
        self.POOL = Pool(len(self.PLAYERS))

        ''' 
        0 - Init
        1 - Preflop
        2 - Flop
        3 - Turn
        4 - River
        5 - Summary
        '''
        self.STAGE = 0 

        def Action():
            print(f'\n当前桌面: {self.TABLE}\n')

            for p in self.PLAYERS:
                over = self.CheckState()
                if over:
                    self.NewGame()
                else:
                    p.Decide()
            
            # match everyone's bet
            for p in self.PLAYERS:
                if p.LASTBET != self.LASTBET:
                    p.Decide()
            
            if self.OFFTABLE:
                self.logger.debug(f'self.OFFTABLE {self.OFFTABLE}')

        # Preflop Action
        self.Preflop()

        self.logger.info(f'盲注开始\n')
        self.SBPLAYER.Bet(self.SB)
        self.BBPLAYER.Bet(self.BB)
        self.logger.info(f'盲注下好\n')

        for p in self.PLAYERS[2:]:
            p.Decide()

        # match everyone's bet
        for p in self.PLAYERS:
            if p.LASTBET != self.LASTBET:
                p.Decide()

        # Flop
        self.Flop()
        Action()
        
        # Turn
        self.Turn()
        Action()

        # River
        self.River()
        Action()

    @property
    def Pool(self):
        #TODO
        return sum(self.POOL.pools[0])

    @property
    def SBPLAYER(self):
        return self.PLAYERS[0]

    @property
    def BBPLAYER(self):
        return self.PLAYERS[1]
    
    @property
    def TABLE(self):
        string = '/'.join(self._raw_table)
        return Table(string)

    def POSITIONS(self):
        '''
        0 - SB
        1 - BB
        2 - UTG
        3 - UTG + 1
        4 - CO
        5 - BT
        '''
        pass

    @property
    def WORLD(self):
        random.shuffle(AI_NAMES)
        result = list(map(lambda x: Player(self, name=x), AI_NAMES))
        random.shuffle(result)
        return set(result)
    
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
            opponent = p.ChooseOpponent()
            if 0.6 < q < 0.9:
                p.Talk('trash', p=opponent)
            elif q > 0.9:
                if opponent.NAME == self.SBPLAYER.NAME:
                    p.Talk(f'建议是弃了😏少损失${self.SB}哈{opponent.NAME}')
                elif opponent.NAME == self.BBPLAYER.NAME:
                    p.Talk(f'哟{opponent.NAME}，这下必须损失${self.BB}了嗷')

    def Deal(self, p):
        p._raw_hand = random.sample(self.RAWCARDS, 2)
        self.logger.debug(f'{p.NAME}拿到手牌{p.HAND}')
 
    def Preflop(self):
        print(f'\n第{self.NUMOFGAMES}局 Preflop阶段\n')
        if self.STAGE == 0:
            for p in self.PLAYERS:
                self.Deal(p)
            self.STAGE = 1
        else:
            self.logger.error(f'self.STAGE should be 0, now {self.STAGE}!')
            raise GameStageError()
        self.logger.debug(f'self.POOL.pools {self.POOL.pools}')

    def Flop(self):
        print(f'\n第{self.NUMOFGAMES}局 Flop阶段\n')
        self.LASTBETPLAYER = None
        self.LASTBET = 0
        if self.STAGE == 1:
            self._raw_table = random.sample(self.RAWCARDS, 3)
            for p in self.PLAYERS:
                p.Combo()
            self.STAGE = 2
        else:
            self.logger.error(f'self.STAGE should be 1, now {self.STAGE}!')
            raise GameStageError()
        self.logger.debug(f'self.POOL.pools {self.POOL.pools}')

    def Turn(self):
        print(f'\n第{self.NUMOFGAMES}局 转牌圈\n')
        self.LASTBETPLAYER = None
        self.LASTBET = 0
        if self.STAGE == 2:
            self._raw_table.append(self.RAWCARDS.pop())
            for p in self.PLAYERS:
                p.Combo()          
            self.STAGE = 3
        else:
            self.logger.error(f'self.STAGE should be 2, now {self.STAGE}!')
            raise GameStageError()
        self.logger.debug(f'self.POOL.pools {self.POOL.pools}')

    def River(self):
        print(f'\n第{self.NUMOFGAMES}局 河牌圈\n')
        self.LASTBETPLAYER = None
        self.LASTBET = 0
        if self.STAGE == 3:
            self._raw_table.append(self.RAWCARDS.pop())
            for p in self.PLAYERS:
                p.Combo()
            self.STAGE = 4
        else:
            self.logger.error(f'self.STAGE should be 3, now {self.STAGE}!')
            raise GameStageError()
        self.logger.debug(f'self.POOL.pools {self.POOL.pools}')

    def Summary(self):
        self.logger.debug(f'self.POOL.pools {self.POOL.pools}')
        if self.STAGE == 4:
            pass

    def CheckState(self):
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
                combos = [p.COMBO for p in self.PLAYERS]
                combos = SortCombo(combos)
                winner = ''
                for p in self.PLAYERS:
                    if p.COMBO == combos[-1]:
                        winner = p
                self.POOL.Give(winner)
                self.OVER = True
            else:
                #TODO side-pool situations
                pass
                self.OVER = True
        return self.OVER

    def Rotate(self):
        r = self.PLAYERS.pop(0)
        self.PLAYERS.append(r)
                
    def Exit(self):
        try:
            sys.exit(0)
        except:
            print('bye👋🏻')
