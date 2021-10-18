# __author__ = arslan
# __date__ = 2021/10/11

import sys
import random
import logging
from typing import List
from thpoker.core import Table

from pool import Pool
from exceptions import *
from world import World
from player import Player
from corpus import CORPUS
from utils import SortCombo
from positions import Positions


class Game():
    
    def __init__(self, n_AI=5, SB=5, buyin=600) -> None:
        self.logger = logging.getLogger('main.game')
        self.WORLD = World(self)
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
        print(f'\n第 {self.NUMOFGAMES} 局')
        self.OVER = False
        self.BLIND = False

        # get on the table dudes
        if self.NUMOFGAMES == 1:
            for i in range(len(self.POSITIONS)-1):
                #self.logger.debug(f'game.NewGame: i {i}')
                p = self.WORLD.pop()
                #self.logger.debug(f'self.WORLD.pop() => {p}')
                p.BuyIn()
                #self.logger.debug(f'self.POSITIONS {self.POSITIONS}')
            # human player get in here
            self.PLAYER.BuyIn()
        else:
            ps = [i for i in self.POSITIONS.__dict__.values() if i]
            for player in ps:
                player.ONTABLE = True
            # rotate, redistribute SB/BB
            self.POSITIONS.Rotate()
            self.logger.info(f'{self.POSITIONS.SB} 小盲')
            self.logger.info(f'{self.POSITIONS.BB} 大盲')
            if self.POSITIONS.AVAILABLE:
                self.WORLD.pop().BuyIn()

        self.LASTBET = self.BB
        self.WINNER = None

        # init Player.HAND and game.TABLE
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

    def Deal(self, p, method='decisive'):
        if method == 'decisive':
            p._raw_hand = random.sample(self.RAWCARDS, 2)
            self.logger.debug(f'{p.NAME}拿到手牌{p.HAND}')
        elif method == 'dynamic':
            pass
 
    def NewRound(self):
        print(f'\n第 {self.NUMOFGAMES} 局 {self.STAGE}\n')
        self.LASTACTION = {}

        if self._stage == 0:
            self.Action()
        elif self._stage == 2:
            self._raw_table = random.sample(self.RAWCARDS, 3)
            self.Action()
        elif self._stage == 5:
            self.Summary()
        else:
            self._raw_table.append(self.RAWCARDS.pop())
            self.Action()

        self.logger.debug(f'self.POOL.pools {self.POOL.pools}')
        input('Press ENTER to continue...\n')

    def Action(self):
        print(f'\n当前桌面: {self.TABLE}\n')

        if self._stage == 0:
            for p in self.PLAYERS:
                p.LASTBET = 0
                if p.SB:
                    p.Bet(self.SB)
                elif p.BB:
                    p.Bet(self.BB)
                    self._stage += 1
                else:
                    p.Decide()
                print(f'-----------------')
        else:
            over = self.CheckState()
            if over:
                self.Summary()
            else:
                for p in self.PLAYERS:
                    self.logger.debug(f'{p.NAME} COMBO: {p.COMBO}')

                    # SB dont forget SB
                    if p.SB and not self.BLIND:
                        p.Bet(self.SB)
                        self.logger.info(f'[SB] {p.NAME} 补上小盲 ${self.SB}')
                        self.BLIND = True

                    # everyone must match their bets
                    if not p.GOOD:
                        p.Decide()
                print(f'-----------------')

        #check if all Players are GOOD or if game over
        self.logger.debug(f'all Players.GOOD? {[p.GOOD for p in self.PLAYERS]}')
        if all([p.GOOD for p in self.PLAYERS]):
            over = self.CheckState()
            if over:
                self.Summary()
            else:
                self._stage += 1
                self.NewRound()
        else:
            self.Action()
        
        input('Press ENTER to continue...\n')

    def Summary(self):
        self.POOL.Give(self.WINNER)
        if self.TABLE:
            print(f'恭喜{self.WINNER.NAME}以{self.WINNER.COMBO}赢得全部底池：${self.POOL}')
        else:
            print(f'恭喜{self.WINNER.NAME}在翻牌前赢得全部底池 ${self.POOL}')

        # losers say bye
        for p in self.PLAYERS:
            if not p.CASH:
                p.Bye()

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
