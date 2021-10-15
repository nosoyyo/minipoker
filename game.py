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


#TODO silent player.Fold() bug fix
#TODO Player.Decide() bug fix
#TODO CLI menu
#TODO winner decide 
#TODO human input
#TODO manual/auto SB raise
#TODO side pool regularization
#TODO SB/BB rotation
#TODO BB preflop raise
#TODO logging
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
    def __init__(self, cash, name=None, is_AI=True) -> None:
        if not name:
            name = 'arslan'
        self.name = name
        self.is_AI = is_AI
        self.hand = []
        self.cash = cash
        self.is_SB = False
        self.is_BB = False

    def __repr__(self) -> str:
        return f'<玩家：{self.name}>'

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

    def Talk(self, command, p=None):
        time.sleep(1)
        if command == 'fold':
            word = random.choice(CORPUS['FOLD'])            
        elif command == 'check':
            word = random.choice(CORPUS['CHECK'])
        elif command == 'call':
            word = random.choice(CORPUS['CALL'])
        elif command == 'raise':
            word = random.choice(CORPUS['RAISE'])
        elif command == 'allin':
            word = random.choice(CORPUS['ALLIN'])
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
            print(f'{self.name}正在决策...')
            s = random.random() + 2
            time.sleep(s)
            logger.debug(f'time.sleep: {s}')

            power = self.PowerCheck() #TODO
            logger.debug(f'power: {power}')
            if self.cash <= game.LASTBET:
                q = random.random()
                if q > 0.5:
                    self.AllIn(game)
                else:
                    self.Fold(game)
            elif power < 20:
                self.Fold(game)
            elif 20 <= power < 40:
                self.Check(game)
            elif 40 <= power < 60:
                self.Call(game)
            elif 60 <= power < 90:
                self.Raise(game)
            elif power >= 90:
                self.AllIn(game)
        else:
            menu = self.MakeUpMenu(game)
            decision = menu.show()
            logger.info(f'you choose: {decision}')

    def MakeUpMenu(self, game):
        #TODO
        #OPTIONS = ['allin','call','check','fold','raise',]
        options = []
        if self.STAGE == 0:
            if self.is_SB:
                options = ['call','fold']
            else:
                options = ['allin','call','fold','raise',]

        logger.info(f'options: {options}')
        return TerminalMenu(options)

    
    def Check(self, game):
        self.Talk('check') #TODO
        game.CHECKED = True
    
    def Call(self, game):
        self.Talk('call')
        bet = game.LASTBET
        self.Bet(bet, game)

    def Raise(self, game):
        self.Talk('raise')
        bet  = game.SB * (int(random.random()*4) + 1) + game.LASTBET
        if bet >= self.cash:
            self.AllIn(game)
        else:
            game.LASTBET = bet
            self.Bet(bet, game)

    def AllIn(self, game):
        self.Talk('allin')
        bet = self.cash
        self.Bet(bet, game)
        game.LASTBET = bet

    def Fold(self, game):
        self.Talk('fold')
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
                p.Talk('trash', p=opponent)
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