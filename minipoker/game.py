# __author__ = arslan
# __date__ = 2021/10/11

from re import M
import sys
import random
import logging
from rich import print
from typing import List
from thpoker.core import Table
from transitions import Machine
from rich.console import Console
from rich.table import Table as RichTable

from minipoker.menu import Menu
from minipoker.pool import Pool
from minipoker.world import World
from minipoker.exceptions import *
from minipoker.player import Player
from minipoker.screen import Screen
from minipoker.utils import GetSeed
from minipoker.positions import Positions


class Game():

    num_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    suit_list = ['s', 'h', 'c', 'd']
    LASTBET = None
    LASTACTION = {}
    STAGES = ['INIT','BLIND','PREFLOP','FLOP','TURN','RIVER','OVER']
    SCREEN = Screen()
    
    def __init__(self, name=None, n_AI=5, SB=5, buyin=600) -> None:
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

        #human player
        name = name or 'arslan'
        self.PLAYER = Player(self, name=name, is_AI=False)

        self.SB = SB
        self.BB = SB*2
        
        self._raw_table = []
        self.RAWCARDS = self.Shuffle()

    @property
    def _check_repeated_cards(self):
        flag = False
        if len(self.CARDSDEALT) == len(set(self.CARDSDEALT)):
            flag = True
        return flag

    def Start(self):
        options = ['♠️ START','♥️ OPTION','♣️ HELP','♦️ ABOUT']
        menu = Menu(options, self, which='table')
        decision = menu.Show()
        if decision == '♠️ START':
            self.NewGame()
        elif decision == '♥️ OPTION':
            options = []
            self.Start()
        elif decision == '♣️ HELP':
            self.Start()
        elif decision == '♦️ ABOUT':
            self.SCREEN.Update('©2021 阿尔斯愣\n MADE WITH ♥️  IN GZ', 'table', 'ABOUT')
            self.Start()
        else:
            # DEBUG
            self.PLAYER.Action(command=decision)
            self.Start()

    @property
    def STATUS(self):
        status = self.__dict__.copy()
        for p in self.POSITIONS.__dict__.values():
            status[p.NAME] = p.__dict__.copy()
        status['POOL'] = self.POOL.__dict__.copy()
        return status

    @property
    def PLAYERS(self):
        ps = [i for i in self.POSITIONS.__dict__.values() if i]
        return [p for p in ps if p.ONTABLE]

    @property
    def ALLPLAYERS(self):
        return [i for i in self.POSITIONS.__dict__.values() if i]

    @property
    def CASHES(self):
        cashes = [p.CASH for p in self.PLAYERS]
        cashes.sort()
        return cashes

    def _init_table(self):
        # get on the table dudes
        if self.NUMOFGAMES == 1:
            for i in range(len(self.POSITIONS)-1):
                p = self.WORLD.pop()
                p.BuyIn()
            # human player get in here
            self.PLAYER.BuyIn()
        else:
            self.logger.debug(f'game.POSITIONS {self.POSITIONS}')
            players = [i for i in self.POSITIONS.__dict__.values() if i]
            for p in players:
                p.ONTABLE = True
                self._total_bet = 0
                p._deactive()
            # rotate, redistribute SB/BB
            self.POSITIONS.Rotate()
            if self.POSITIONS.AVAILABLE:
                self.WORLD.pop().BuyIn()

        # init or re-init POOL
        self.POOL = Pool(self)

    def _init_game(self):
        self.NUMOFGAMES += 1
        self.OVER = False
        self.LASTBET = self.BB
        self.WINNERS = []
        self._stage = 0
        self._raw_table = []
        self.CARDSDEALT = []

    def _init_deck(self):
        self.RAWCARDS = self.Shuffle()

        # init Player.HAND and game.TABLE
        for p in self.PLAYERS:
            p._raw_hand = []  
            p._raw_hand.append(self.Deal())
            p._raw_hand.append(self.Deal())
            self.logger.debug(f'{p.NAME}拿到手牌{p.HAND}')

    def NewGame(self) -> None:

        self._init_game()
        self._init_table()
        self._init_deck()

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
        random.seed(GetSeed())
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
            random.seed(GetSeed())
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
        self.logger.debug(f'game._check_repeated_cards {self._check_repeated_cards}')

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

    def Actions(self):
        self.logger.debug(f'本轮下注 {self.POOL.CURRENT}')
        self.POOL.Show()

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
                        p._active()
                        p.Decide()
                        if p.state != 'FOLD':
                            # player here might fold already
                            # but `ONTABLE` was not refreshed
                            # so `_deactive()` cannot be called
                            p._deactive()
 
                over = self.CheckState()
                if over:
                    self.Summary()
        else:
            for p in self.PLAYERS:
                self.logger.debug(f'{p.NAME} COMBO: {p.COMBO}')

                if not p.GOOD and p.ONTABLE:
                    p._active()
                    p.Decide()
                    if p.state != 'FOLD':
                        p._deactive()

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
                self.logger.debug(self.POOL.Show())
                self._stage += 1
                self.NewRound()
        else:
            self.Actions()

    def Summary(self, debug=False):
        self.POOL.Account()
        if len(self.WINNERS) == 1:
            WINNER = self.WINNERS[0]
            share = self.POOL
            # TODO update `ShowHand` to somewhere
            if self._stage > 1:
                for p in self.PLAYERS:
                    p.ShowHand()
                content = f'恭喜{WINNER.NAME}以{WINNER.COMBO}赢得全部底池 {share}'
            else:
                content = f'恭喜{WINNER.NAME}在翻牌前赢得全部底池 {share}'
        else:
            winners = '、'.join([p.NAME for p in self.WINNERS])
            share = int(self.POOL.SUM / len(self.WINNERS))
            content = f'恭喜{winners}平分底池 {self.POOL}，每人获得 ${share}'
            
        self.SCREEN.Update(content, 'title')

        # update `Layout['table']`
        for p in self.WINNERS:
            p.LASTACTION = f'赢得 {share}'
        self.POOL.Show()

        if not debug:
            # losers say bye
            for p in self.POSITIONS.__dict__.values():
                if not p.CASH:
                    self.logger.debug(f'{p} got no cash({p.CASH}) and get off table')
                    self.logger.debug(f'game.POSITIONS {self.POSITIONS}')
                    self.logger.debug(f'game.PLAYERS {self.PLAYERS}')
                    self.logger.debug(f'p.ONTABLE {p.ONTABLE}')
                    p.Bye()
                #clean up the pool
                if p._total_bet:
                    p._total_bet = 0

            def _end_menu():
                options = ['下一局', '离开',] 
                menu = Menu(options, self)
                decision = menu.Show()
                if decision == '下一局':
                    self.NewGame()
                elif decision == '离开':
                    self.Exit()
                else:
                    self.PLAYER.Action(command=decision)
                    _end_menu()

            _end_menu()

    def CheckState(self):
        '''
        check winner and allocate money
        '''
        if len(self.PLAYERS) == 1:
            if len(self.POOL) == 1:
                self.WINNERS.append(self.PLAYERS[0])
                self.OVER = True
            else:
                #TODO side-pool situations
                pass
                self.OVER = True
        elif self._stage == 4:
            if len(self.POOL) == 1:
                self.WINNERS = self.Elect()
                self.OVER = True
            else:
                #TODO side-pool situations
                pass
                self.OVER = True
        return self.OVER

    def Elect(self, players=None) -> list:
        '''
        Elect a winner from several given players
        by comparing their `Combo`
        '''
        players = players or self.PLAYERS
        result = []
        combos = [p.COMBO for p in players]
        #combos = SortCombo(combos)
        # multi winner situation considered, `SortCombo` not needed
        for p in players:
            if p.COMBO == max(combos):
                result.append(p)
        return result

    def Exit(self):
        sys.exit('bye👋🏻')
