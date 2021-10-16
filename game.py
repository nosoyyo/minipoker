# __author__ = arslan
# __date__ = 2021/10/11

import sys
import random
import logging

from exceptions import *
from player import Player
from utils import CORPUS, AI_NAMES, ShowHand, SortCombo


class Pool:

    def __init__(self, n_players) -> None:
        self.pools = [[0]]
        self.pools = [[i for i in self.pools[0] for j in range(n_players)]]
    
    def __len__(self) -> int:
        return len(self.pools)
    
    def __repr__(self) -> str:
        #TODO
        return str(sum(self.pools[0]))

    def Add(self, p: Player, game, bet: int, index=0) -> None:
        pindex = p.GetSelfIndex(game)
        self.pools[index][pindex] += bet
        self.ShowPool(p, bet)

    def Give(self, p, index=0):
        p.cash += sum(self.pools[index])
        print(f'{p.name}赢了全部底池：${sum(self.pools[index])}')
        # here we do no clean, will do Pool.__init__ later in NewGame()

    def Side(self, bet: int, index)-> None:
        #TODO
        pass

    def ShowPool(self, p: Player, bet)-> None:
        print(f'{p.name}下注 ${bet}，剩余现金 ${p.cash}')
        if len(self.pools) == 1:
            print(f'目前底池 ${sum(self.pools[0])}')
        else:
            #TODO
            pass


class Game():
    
    def __init__(self, n_AI=5, SB=5, buyin=600):
        self.logger = logging.getLogger('main.game')

        self.BUYIN = buyin
        self.NUMOFGAMES = 0
        self.TABLE = []
        self.RawCards = self.Shuffle()
        self.SB = SB
        self.BB = SB*2

        self.PLAYER = Player(cash=buyin, is_AI=False)
        self.MakeUpAI(n_AI, buyin)
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
            if 0.6 < q < 0.9:
                p.Talk(self, 'trash', p=opponent)
            elif q > 0.9:
                if opponent.name == self.SBPLAYER.name:
                    p.Talk(self, f'建议是弃了😏少损失${self.SB}哈{opponent.name}')
                elif opponent.name == self.BBPLAYER.name:
                    p.Talk(self, f'哟{opponent.name}，这下必须损失${self.BB}了嗷')

    def BuyIn(self):
        for p in self.PLAYERS:
            if not p.cash:
                q = random.random()
                if q > 0.5:
                    p.BuyIn(self)
                else:
                    p.Bye(self)

    def Deal(self, player):
        card1 = self.RawCards.pop()
        card2 = self.RawCards.pop()
        self.logger.debug(f'给{player.name}发了一张{card1}')
        self.logger.debug(f'给{player.name}发了一张{card2}\n')
        player.hand.append(card1)
        player.hand.append(card2)
 
    def Preflop(self):
        print(f'\n第{self.NUMOFGAMES}局 Preflop阶段\n')
        if self.STAGE == 0:
            for i in range(len(self.PLAYERS)):
                self.Deal(self.PLAYERS[i])
            self.STAGE = 1
        else:
            self.logger.error(f'game.STAGE should be 0, now {self.STAGE}!')
            raise GameStageError()

    def Flop(self):
        print('\n第{self.NUMOFGAMES}局 Flop阶段\n')
        self.LASTBET = 0
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

    def Turn(self):
        print('\n第{self.NUMOFGAMES}局 转牌圈\n')
        self.LASTBET = 0
        if self.STAGE == 2:
            self.TABLE.append(self.RawCards.pop())
            ShowHand(self.TABLE)
            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Combo(self)          
            self.STAGE = 3

        else:
            self.logger.error(f'game.STAGE should be 2, now {self.STAGE}!')
            raise GameStageError()

    def River(self):
        print('\n第{self.NUMOFGAMES}局 河牌圈\n')
        self.LASTBET = 0
        if self.STAGE == 3:
            self.TABLE.append(self.RawCards.pop())
            ShowHand(self.TABLE)
            for i in range(len(self.PLAYERS)):
                self.PLAYERS[i].Combo(self)
            self.STAGE = 4
        else:
            self.logger.error(f'game.STAGE should be 3, now {self.STAGE}!')
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
        return self.OVER

    def Rotate(self):
        r = self.PLAYERS.pop(0)
        self.PLAYERS.append(r)
                
    def Exit(self):
        try:
            sys.exit(0)
        except:
            print('bye👋🏻')

