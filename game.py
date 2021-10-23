# __author__ = arslan
# __date__ = 2021/10/11

import sys
import random
import logging
from rich import print
from typing import List
from thpoker.core import Table
from transitions import Machine
from rich.console import Console
from rich.table import Table as RichTable

from pool import Pool
from world import World
from exceptions import *
from player import Player
from screen import Screen
from utils import SortCombo
from positions import Positions


class Game():

    num_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    suit_list = ['s', 'h', 'c', 'd']
    LASTBET = None
    LASTACTION = {}
    STAGES = ['INIT','BLIND','PREFLOP','FLOP','TURN','RIVER','OVER']
    SCREEN = Screen()
    
    def __init__(self, n_AI=5, SB=5, buyin=600) -> None:
        self.logger = logging.getLogger('main.game')
        self.console = Console()
        self.machine = Machine(model=self, states=self.STAGES, initial='INIT')
        self.machine.add_ordered_transitions(loop=False)
        self.machine.add_transition(trigger='Over', source='*', dest='OVER')
        self.machine.add_transition(trigger='ReInit', source='*', dest='INIT')

        self.WORLD = World(self)

        self.POSITIONS = Positions(n_AI)
        self.BUYIN = buyin
        self.NUMOFGAMES = 0

        self.PLAYER = Player(self, is_AI=False)

        self.SB = SB
        self.BB = SB*2
        
        self._raw_table = []
        self.RAWCARDS = self.Shuffle()
        self.CARDSDEALT = []

    @property
    def STATUS(self):
        status = self.__dict__.copy()
        for p in self.POSITIONS.__dict__.values():
            status[p.NAME] = p.__dict__
        status['POOL'] = self.POOL.__dict__
        return status

    @property
    def PLAYERS(self):
        ps = [i for i in self.POSITIONS.__dict__.values() if i]
        return [p for p in ps if p.ONTABLE]

    @property
    def CASHES(self):
        cashes = [p.CASH for p in self.PLAYERS]
        cashes.sort()
        return cashes

    def NewGame(self) -> None:

        self.NUMOFGAMES += 1
        print(f'\n第 {self.NUMOFGAMES} 局')
        self.OVER = False
        self.BLIND = False

        # get on the table dudes
        if self.NUMOFGAMES == 1:
            for i in range(len(self.POSITIONS)-1):
                p = self.WORLD.pop()
                p.BuyIn()
            # human player get in here
            self.PLAYER.BuyIn()
        else:
            self.logger.debug(f'game.POSITIONS {self.POSITIONS}')
            ps = [i for i in self.POSITIONS.__dict__.values() if i]
            for player in ps:
                player.ONTABLE = True
            # rotate, redistribute SB/BB
            self.POSITIONS.Rotate()
            if self.POSITIONS.AVAILABLE:
                self.WORLD.pop().BuyIn()

            self.logger.info(f'{self.POSITIONS.SB} 小盲')
            self.logger.info(f'{self.POSITIONS.BB} 大盲')

        self.LASTBET = self.BB
        self.WINNER = None

        self._raw_table = []
        self.CARDSDEALT = []
        self.RAWCARDS = self.Shuffle()

        # init Player.HAND and game.TABLE
        for p in self.PLAYERS:
            p._raw_hand = []  
            p._raw_hand.append(self.Deal())
            p._raw_hand.append(self.Deal())
            self.logger.debug(f'{p.NAME}拿到手牌{p.HAND}')

        # init or re-init POOL
        self.POOL = Pool(self)

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
        RawCards = [x + y for x in self.num_list for y in self.suit_list]
        random.shuffle(RawCards)
        return RawCards

    def Deal(self, method='decisive'):
        '''
        :return: a single card in raw form like 'As'
        '''
        if method == 'decisive':
            self.logger.debug(f'dealing card with `decisive` method')
            card = self.RAWCARDS.pop()
            if card in self.CARDSDEALT:
                self.Deal('decisive')
            self.CARDSDEALT.append(card)
            return self.RAWCARDS.pop()
     
        elif method == 'dynamic':
            self.logger.debug(f'dealing card with `dynamic` method')
            random.shuffle(self.num_list)
            random.shuffle(self.suit_list)
            card = random.choice(self.num_list) + random.choice(self.suit_list)
            if card in self.CARDSDEALT:
                self.Deal('dynamic')
            self.CARDSDEALT.append(card)
            return card
 
    def ShowTable(self):
        if self.TABLE:
            GRID = RichTable.grid(expand=True) 
            GRID.add_column() 
            GRID.add_column(justify="centre") 
            GRID.add_row(f'当前桌面 [bold magenta]{self.TABLE}')
            self.console.print(GRID)

    def NewRound(self):       
        
        self.logger.info(f'\n第 {self.NUMOFGAMES} 局 {self.STAGE}\n')
        self.ShowTable()
        ontable = '、'.join([p.NAME for p in self.PLAYERS])
        self.logger.info(f'当前玩家 {ontable}')

        # re-init stuff if necessary
        self.LASTBET = 0
        self.LASTACTION = {}
        for p in self.PLAYERS:
            if not p.ALLIN:
                p.GOOD = False
                p.LASTACTION = None
                p.LASTBET = 0

        if self._stage == 0:
            self.Actions()
        elif self._stage == 2:
            # method == decisive
            self._raw_table.append(self.Deal())
            self._raw_table.append(self.Deal())
            self._raw_table.append(self.Deal())

            self.Actions()
        elif 2 < self._stage < 5:
            self._raw_table.append(self.RAWCARDS.pop())
            self.Actions()
        elif self._stage == 5:
            self.Actions()
            self.Summary()

        self.logger.debug(f'self.POOL.pools {self.POOL.pools}')
        #input('Press ENTER to continue...\n')

    def Actions(self):
        self.logger.debug(f'本轮下注 {self.POOL.CURRENT}')

        if self._stage == 0:
            for p in self.PLAYERS:
                # p.LASTBET = 0
                if p.SB:
                    p.Bet(self.SB)
                    p.LASTACTION = '小盲'
                elif p.BB:
                    p.Bet(self.BB)
                    p.LASTACTION = '大盲'
                    self._stage += 1
                else:
                    if p.ONTABLE:
                        p.Active()
                        p.Decide()
                        p.Deactive()

                over = self.CheckState()
                if over:
                    self.Summary()

                #self.POOL.ShowCurrent()
        else:
            for p in self.PLAYERS:
                self.logger.debug(f'{p.NAME} COMBO: {p.COMBO}')

                if not p.GOOD and p.ONTABLE:
                    p.Active()
                    p.Decide()
                    p.Deactive()
                    over = self.CheckState()
                    if over:
                        self.Summary()

        #check if all Players are GOOD or if game over
        self.logger.debug(f'all Players.GOOD? {[p.GOOD for p in self.PLAYERS]}')
        if all([p.GOOD for p in self.PLAYERS]):
            over = self.CheckState()
            if over:
                self.Summary()
            else:
                # accounting
                self.POOL.Account()
                self.logger.debug('game.POOL.Account() =>')
                print(self.POOL)
                self.logger.debug(self.POOL.Show())
                #input('\n\nPress ENTER to continue...\n')
                self._stage += 1
                self.NewRound()
        else:
            self.Actions()
        
        #input('Press ENTER to continue...\n')

    def Summary(self):
        self.POOL.Account()
        if self._stage > 1:
            if len(self.PLAYERS) > 1:
                for p in self.PLAYERS:
                    p.ShowHand()
                print(f'恭喜{self.WINNER.NAME}以{self.WINNER.COMBO}赢得全部底池 {self.POOL}')
            else:
                print(f'恭喜{self.WINNER.NAME}赢得全部底池 {self.POOL}')
        else:
            print(f'恭喜{self.WINNER.NAME}在翻牌前赢得全部底池 {self.POOL}')
        #input('Press ENTER to continue...\n')

        # losers say bye
        for p in self.PLAYERS:
            if not p.CASH:
                self.logger.debug(f'{p} got no cash({p.CASH}) and get off table')
                self.logger.debug(f'game.POSITIONS {self.POSITIONS}')
                self.logger.debug(f'game.PLAYERS {self.PLAYERS}')
                self.logger.debug(f'p.ONTABLE {p.ONTABLE}')
                p.Bye()

        #input('Press ENTER to continue...\n')
        self.NewGame()

    def CheckState(self):
        '''
        check winner and allocate money
        '''
        if len(self.PLAYERS) == 1:
            if len(self.POOL) == 1:
                self.WINNER = self.PLAYERS[0]
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
        sys.exit('bye👋🏻')
