# __author__ = arslan
# __date__ = 2021/10/11

import time
import random
import logging
from simple_term_menu import TerminalMenu
from thpoker.core import Hand, Table, Combo, Cards

from exceptions import *
from utils import CORPUS, AI_NAMES


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#TODO CLI menu
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


class Player():
    def __init__(self, cash, name=None, is_AI=True,) -> None:
        if not name:
            name = 'arslan'
        self.name = name
        self.is_AI = is_AI
        self.hand = []
        self.cash = cash
        self.is_SB = False
        self.is_BB = False
        self.index = None

    def __repr__(self) -> str:
        return f'<玩家：{self.name}>'
    
    def _getSelfIndex(self, game):
        for i in range(len(game.PLAYERS)):
            if self.name == game.PLAYERS[i].name:
                self.index = i

    def ShowHand(self) -> Hand:
        string = ''
        for i in range(len(self.hand)):
            string += self.hand[i] + '/'
        return(Hand(string))

    def Bet(self, bet, game) -> Pool:
        if self.cash < bet:
            raise OverBetError(f'不能下这些，你只有{self.cash}了')
        else:
            self.cash -= bet
            game.POOL.Add(self.name, bet)
        return game.POOL

    def Talk(self, game, command, p=None):
        time.sleep(1)
        if command == 'fold':
            word = random.choice(CORPUS['FOLD'])      
            self.Fold(game)      
        elif command == 'check':
            word = random.choice(CORPUS['CHECK'])
            self.Check(game)
        elif command == 'call':
            word = random.choice(CORPUS['CALL'])
            self.Call(game)
        elif command == 'raise':
            word = random.choice(CORPUS['RAISE'])
            self.Raise(game)
        elif command == 'allin':
            word = random.choice(CORPUS['ALLIN'])
            self.AllIn(game)
        elif command == 'trash':
            trash = random.choice(CORPUS['TRASHTALK'])
            word = f'{trash}{p.name}'
        print(f'{self.name}：{word}')

    def Combo(self, game) -> Combo:
        self.combo = Combo(hand=self.ShowHand(), table=ShowHand(game.TABLE))
        logger.debug(f'{self.name}的combo：{self.combo}')
        return self.combo

    def PowerCheck(self):
        # flush check
        # ace check
        # TODO
        power = int(random.random() * 100)
        return power
    
    def ChooseOpponent(self, game):
        opponent = random.choice(game.PLAYERS)
        if opponent.name == self.name:
            opponent = self.ChooseOpponent(game)
        return opponent

    def Decide(self, game):
        if self.is_AI:
            if not self.cash:
                logger.info(f'{self.name}无筹码，跳过此轮')
                pass
            else:
                print(f'{self.name}正在决策...')
                s = random.random() + 2
                time.sleep(s)
                logger.debug(f'time.sleep: {s}')

                power = self.PowerCheck() #TODO
                logger.debug(f'power: {power}')

                if self.cash <= game.LASTBET:
                    q = random.random()
                    logger.debug(f'{self.name}现金:{self.cash}，当前下注{game.LASTBET}')
                    if q > 0.5:                        
                        self.Talk(game, 'allin')
                    else:
                        self.Talk(game, 'fold')
                elif power < 20:
                    self.Talk(game, 'fold')
                elif 20 <= power < 40:
                    if not game.LASTBET:
                        self.Talk(game, 'check')
                    else:
                        self.Talk(game, 'fold')
                elif 40 <= power < 60:
                    self.Talk(game, 'call')
                elif 60 <= power < 90:
                    self.Talk(game, 'raise')
                elif power >= 90:
                    self.Talk(game, 'allin')
        else:
            if not self.cash:
                pass
            else:
                options = self.Options(game)
                menu = TerminalMenu(options)
                decision = menu.show()
                decision = options[decision]
                logger.info(f'you choose: {decision}')
                self.Talk(game, decision)

    def Options(self, game):
        # options = ['allin','call','check','fold','raise',]
        options = []
        if game.LASTBET >= self.cash:
            options = ['allin', 'fold']
        else:
            if game.STAGE == 0:
                if self.is_SB:
                    options = ['call','fold']
                else:
                    options = ['call','raise','allin','fold',]
            else:
                if not game.LASTBET:
                    options = ['call','check','raise','allin','fold',]
                else:
                    options = ['call','raise','allin','fold',]

        logger.info(f'options: {options}')
        return options

    
    def Check(self, game):
        game.CHECKED = True
    
    def Call(self, game):
        bet = game.LASTBET
        self.Bet(bet, game)

    def Raise(self, game):
        bet  = game.SB * (int(random.random()*4) + 1) + game.LASTBET
        if bet >= self.cash:
            self.Talk(game, 'allin')
        else:
            game.LASTBET = bet
            self.Bet(bet, game)

    def AllIn(self, game):
        bet = self.cash
        self.Bet(bet, game)
        game.LASTBET = bet

    def Fold(self, game):
        for i in range(len(game.PLAYERS)+1):
            if self.name == game.PLAYERS[i].name:
                game.PLAYERS.pop(i)
                print(f'{self.name}离开牌桌，还剩{len(game.PLAYERS)}家\n')
                logger.debug(f'game.PLAYERS = {game.PLAYERS}')
                break


class Game():
    
    def __init__(self, n_AI=5, SB=5, cash=600):
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
        logger.debug(f'给{player.name}发了一张{card1}')
        logger.debug(f'给{player.name}发了一张{card2}\n')
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
            logger.error(f'game.STAGE should be 0, now {self.STAGE}!')
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
            logger.error(f'game.STAGE should be 1, now {self.STAGE}!')
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
            logger.error(f'game.STAGE should be 2, now {self.STAGE}!')
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
            logger.error(f'game.STAGE should be 3, now {self.STAGE}!')
            raise GameStageError()

        print(f'current TABLE: {self.TABLE}\n')

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

    # Preflop
    game.Preflop()

    for p in game.PLAYERS:
        if p.is_SB:
            game.POOL = p.Bet(game.SB, game)
        elif p.is_BB:
            game.POOL = p.Bet(game.BB, game)
        else:
            p.Decide(game)

    # Flop
    game.Flop()
    for p in game.PLAYERS:
        p.Decide(game)
    
    # Turn
    game.Turn()
    for p in game.PLAYERS:
        p.Decide(game)

    # River
    game.River()
    for p in game.PLAYERS:
        p.Decide(game)