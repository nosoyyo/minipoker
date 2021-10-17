# __author__ = arslan
# __date__ = 2021/10/11

import sys
import random
import logging
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

    def Give(self, p, index=0):
        p.CASH += sum(self.pools[index])
        print(f'{p.NAME}赢了全部底池：${sum(self.pools[index])}')
        # here we do no clean, will do Pool.__init__ later in NewGame()

    def Side(self, bet: int, index)-> None:
        #TODO
        pass

    def ShowPool(self, p: Player, bet)-> None:
        print(f'{p.NAME}下注 ${bet}，剩余现金 ${p.CASH}')
        if len(self.pools) == 1:
            print(f'目前底池 ${sum(self.pools[0])}')
        else:
            #TODO
            pass


class Game():
    
    def __init__(self, n_AI=5, SB=5, buyin=600):
        self.logger = logging.getLogger('main.self')

        self.BUYIN = buyin
        self.NUMOFGAMES = 0
        self._raw_table = []
        self.RAWCARDS = self.Shuffle()
        self.SB = SB
        self.BB = SB*2

        self.PLAYER = Player(self, is_AI=False)
        self.MakeUpAI(n_AI)
        self.WAITLIST = []
        self.PLAYERS = self.AI + [self.PLAYER]
        random.shuffle(self.PLAYERS)
        self.POOL = Pool(len(self.PLAYERS))

        # distribue SB and BB
        self.Rotate()

        ''' 
        0 - Init
        1 - Preflop
        2 - Flop
        3 - Turn
        4 - River
        5 - Summary
        '''
        self.STAGE = 0

        self.LASTBET = self.BB
        self.WINNER = None
        self.OVER = False

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

    def MakeUpAI(self, n_AI):
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
        result = list(map(lambda x: Player(self, name=x), result))
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
            opponent = p.ChooseOpponent()
            if 0.6 < q < 0.9:
                p.Talk('trash', p=opponent)
            elif q > 0.9:
                if opponent.NAME == self.SBPLAYER.NAME:
                    p.Talk(f'建议是弃了😏少损失${self.SB}哈{opponent.NAME}')
                elif opponent.NAME == self.BBPLAYER.NAME:
                    p.Talk(f'哟{opponent.NAME}，这下必须损失${self.BB}了嗷')

    def BuyIn(self):
        for p in self.PLAYERS:
            if not p.CASH:
                q = random.random()
                if q > 0.5:
                    p.BuyIn()
                else:
                    p.Bye()

    def Deal(self, player):
        card1 = self.RAWCARDS.pop()
        self.logger.debug(f'给{player.NAME}发了一张{card1}')
        player.Draw(card1)
        card2 = self.RAWCARDS.pop()
        self.logger.debug(f'给{player.NAME}发了一张{card2}\n')
        player.Draw(card2)
 
    def Preflop(self):
        print(f'\n第{self.NUMOFGAMES}局 Preflop阶段\n')
        if self.STAGE == 0:
            for p in self.PLAYERS:
                self.Deal(p)
            self.STAGE = 1
        else:
            self.logger.error(f'self.STAGE should be 0, now {self.STAGE}!')
            raise GameStageError()

    def Flop(self):
        print(f'\n第{self.NUMOFGAMES}局 Flop阶段\n')
        self.LASTBET = 0
        if self.STAGE == 1:
            card1 = self.RAWCARDS.pop()
            card2 = self.RAWCARDS.pop()
            card3 = self.RAWCARDS.pop()
            self._raw_table = [card1, card2, card3]
            for p in self.PLAYERS:
                p.Combo()
            self.STAGE = 2
        else:
            self.logger.error(f'self.STAGE should be 1, now {self.STAGE}!')
            raise GameStageError()

    def Turn(self):
        print(f'\n第{self.NUMOFGAMES}局 转牌圈\n')
        self.LASTBET = 0
        if self.STAGE == 2:
            self._raw_table.append(self.RAWCARDS.pop())
            for p in self.PLAYERS:
                p.Combo()          
            self.STAGE = 3

        else:
            self.logger.error(f'self.STAGE should be 2, now {self.STAGE}!')
            raise GameStageError()

    def River(self):
        print(f'\n第{self.NUMOFGAMES}局 河牌圈\n')
        self.LASTBET = 0
        if self.STAGE == 3:
            self._raw_table.append(self.RAWCARDS.pop())
            for p in self.PLAYERS:
                p.Combo()
            self.STAGE = 4
        else:
            self.logger.error(f'self.STAGE should be 3, now {self.STAGE}!')
            raise GameStageError()

    def Summary(self):
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


    def NewGame(self):

        self.NUMOFGAMES += 1
        print(f'\n第{self.NUMOFGAMES}局')

        self.OVER = False
        self.PLAYERS += self.WAITLIST
        self.WAITLIST = []
        for p in self.PLAYERS:
            p._raw_hand = []

        self._raw_table = []
        self.RAWCARDS = self.Shuffle()

        # init or re-init POOL
        self.POOL = Pool(len(self.PLAYERS))

        # must before self.Rotate()
        self.BuyIn()

        # distribute SB/BB
        self.Rotate()
        self.logger.info(f'{self.PLAYERS[0]}小盲')
        self.logger.info(f'{self.PLAYERS[1]}大盲')

        self.TrashTalk()

        self.LASTBET = self.BB
        self.STAGE = 0
        self.WINNER = None

        def Action():
            print(f'\n当前桌面: {self.TABLE}\n')

            for p in self.PLAYERS:
                over = self.CheckState()
                if over:
                    self.NewGame()
                else:
                    p.Decide()
            
            if self.WAITLIST:
                self.logger.debug(f'self.WAITLIST {self.WAITLIST}')

        # Preflop
        self.Preflop()

        self.SBPLAYER.Bet(self.SB)
        self.BBPLAYER.Bet(self.BB)

        for p in self.PLAYERS[2:]:
            p.Decide()

        for p in self.PLAYERS[:2]:
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
