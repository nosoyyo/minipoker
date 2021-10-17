# __author__ = arslan
# __date__ = 2021/10/11

import sys
import random
import logging
from typing import List
from thpoker.core import Table

from pool import Pool
from exceptions import *
from player import Player
from positions import Positions
from world import World
from utils import CORPUS, SortCombo


class Game():
    
    def __init__(self, n_AI=5, SB=5, buyin=600) -> None:
        self.logger = logging.getLogger('main.self')
        self.WORLD = World()
        self.POSITIONS = Positions(n_AI)
        self.BUYIN = buyin
        self.NUMOFGAMES = 0
        self._raw_table = []
        self.RAWCARDS = self.Shuffle()
        self.SB = SB
        self.BB = SB*2

        self.PLAYER = Player(self, is_AI=False)
    
    @property
    def PLAYERS(self):
        ps = [i for i in self.POSITIONS.__dict__.values() if i]
        return [p for p in ps if p.ONTABLE]

    def NewGame(self) -> None:

        self.NUMOFGAMES += 1
        print(f'\n第{self.NUMOFGAMES}局')
        self.OVER = False
        
        if self.NUMOFGAMES == 1:
            for i in range(len(self.POSITIONS)-1):
                #self.logger.debug(f'self.WORLD {self.WORLD}')
                p = self.WORLD.pop()
                #self.logger.debug(f'p {p}')
                p.BuyIn()
            # human player get in here
            self.PLAYER.BuyIn()
        else:
            if self.POSITIONS.AVAILABLE:
                self.WORLD.pop().BuyIn()

        # distribute SB/BB
        self.POSITIONS.Rotate()
        self.logger.info(f'{self.POSITIONS.SB} 小盲')
        self.logger.info(f'{self.POSITIONS.BB} 大盲')

        self.LASTBET = self.BB
        self.WINNER = None

        for p in self.PLAYERS:
            p._raw_hand = []  
            self.Deal(p)
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
        self._stage = 0 

        self.NewRound()

    @property
    def Pool(self):
        #TODO
        return sum(self.POOL.pools[0])

    @property
    def TABLE(self):
        string = '/'.join(self._raw_table)
        return Table(string)
    
    @property
    def STAGE(self):
        _dict = {
            0 : '盲注阶段',
            1 : 'Preflop阶段',
            2 : 'Flop',
            3 : '转牌圈',
            4 : '河牌圈',
            5 : '此局结束',
        }
        return _dict[self._stage]
    
    def Shuffle(self):
        num_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        suit_list = ['s', 'h', 'c', 'd']
        RawCards = [x + y for x in num_list for y in suit_list]
        random.shuffle(RawCards)
        return RawCards

    def Deal(self, p):
        p._raw_hand = random.sample(self.RAWCARDS, 2)
        self.logger.debug(f'{p.NAME}拿到手牌{p.HAND}')
 
    def NewRound(self):
        print(f'\n第{self.NUMOFGAMES}局 {self.STAGE}\n')
        self.LASTBETPLAYER = None
        self.LASTBET = 0

        if self._stage == 0:
            self.logger.info(f'盲注开始\n')
            self.POSITIONS.SB.Bet(self.SB)
            self.POSITIONS.BB.Bet(self.BB)
            self.logger.info(f'盲注下好\n')
            self.Action()
        elif self._stage == 1:
            self._raw_table = random.sample(self.RAWCARDS, 3)
            self.Action()
        elif self._stage == 5:
            self.Summary()
        else:
            self._raw_table.append(self.RAWCARDS.pop())
            self.Action()

        self._stage += 1
        self.logger.debug(f'self.POOL.pools {self.POOL.pools}')

    def Action(self):
        print(f'\n当前桌面: {self.TABLE}\n')

        for p in self.PLAYERS:
            p.LASTBET = 0
            over = self.CheckState()
            if over:
                self.Summary()
                self.NewGame()
            else:
                p.Decide()
        
        # match everyone's bet
        for p in self.PLAYERS:
            while not self.POOL.EVEN:
                p.Decide()
                if self.POOL.EVEN:
                    break

    def Summary(self):
        self.POOL.Give(self.WINNER)
        print(f'恭喜{self.WINNER.NAME}以{self.WINNER.COMBO}赢得全部底池：${self.POOL}')
        input('Press ENTER to continue...\n')
        self.NewGame()

    def CheckState(self):
        '''
        check winner and allocate money
        '''
        if len(self.PLAYERS) == 1:
            if len(self.POOL) == 1:
                self.WINNER = self.PLAYERS[0]
                self.POOL.Give(self.WINNER)
                self.OVER = True
            else:
                #TODO side-pool situations
                pass
                self.OVER = True
        elif self._stage == 4:
            if len(self.POOL) == 1:
                combos = [p.COMBO for p in self.PLAYERS]
                combos = SortCombo(combos)
                for p in self.PLAYERS:
                    if p.COMBO == combos[-1]:
                        self.WINNER = p
                self.OVER = True
            else:
                #TODO side-pool situations
                pass
                self.OVER = True
        return self.OVER
                
    def Exit(self):
        try:
            sys.exit(0)
        except:
            print('bye👋🏻')
