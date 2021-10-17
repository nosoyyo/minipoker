import time
import random
import logging
from thpoker.core import Hand, Combo
from simple_term_menu import TerminalMenu

from utils import CORPUS
from exceptions import GameAlreadyFullError, OverBetError, PlayerIndexError, BuyInError


class Player():
    def __init__(self, game, name=None, is_AI=True,) -> None:
        self.logger = logging.getLogger('main.player')

        self.game = game

        if not name:
            name = 'arslan'
        self.NAME = name
        self.IS_AI = is_AI
        self._raw_hand = [] #:List:
        self.CASH = 0
        self.COMBO = None
        self.BUYINTIMES = 0
        self.LASTBET = 0
        self.ONTABLE = False

    def __repr__(self) -> str:
        info = f'<{self.NAME} 总盈亏${self.WEALTH} 筹码${self.CASH}>'
        if self.INDEX:
            info = f'{self.INDEX}: {info}'
        return info

    @property
    def WEALTH(self):
        return self.CASH - (self.game.BUYIN * self.BUYINTIMES)
    
    @property
    def INDEX(self) -> int:
        try:
            for i in range(len(self.game.PLAYERS)):
                if self.NAME == self.game.PLAYERS[i].NAME:
                    return i
        except:
            return None

    @property
    def HAND(self):
        string = '/'.join(self._raw_hand)
        return(Hand(string))

    @property
    def _hand_power(self):
        for c in self._raw_hand:
            pass

    def Bet(self, bet):
        if self.CASH < bet:
            raise OverBetError(f'{self.NAME}不能下注 ${bet}，筹码只剩 ${self.CASH} 了')
        else:
            self.CASH -= bet
            self.game.POOL.Add(self, bet)
            self.game.LASTBETPLAYER = self
            self.LASTBET = bet
        return self.game.POOL

    def Talk(self, command, p=None):
        time.sleep(0.3)
        if command == 'fold':
            word = random.choice(CORPUS['FOLD'])      
            self.Fold()      
        elif command == 'check':
            word = random.choice(CORPUS['CHECK'])
            self.Check()
        elif command == 'call':
            word = random.choice(CORPUS['CALL'])
            self.Call()
        elif command == 'raise':
            word = random.choice(CORPUS['RAISE'])
            oindex = self.INDEX + 1
            if oindex > len(self.game.PLAYERS) - 2:
                oindex = 0
            opponent = self.game.PLAYERS[oindex]
            word = f'{word}，敢跟吗{opponent.NAME}'
            self.Raise()
        elif command == 'allin':
            word = random.choice(CORPUS['ALLIN'])
            self.AllIn()
        elif command == 'trash':
            trash = random.choice(CORPUS['TRASHTALK'])
            word = f'{trash}{p.NAME}'
        elif command == 'buyin':
            word = random.choice(CORPUS['BUYIN'])
        elif command == 'bye':
            word = random.choice(CORPUS['BYE'])
        else:
            word = command
        print(f'{self.NAME}：{word}\n')

    def Combo(self) -> Combo:
        self.COMBO = Combo(hand=self.HAND, table=self.game.TABLE)
        return self.COMBO
 
    def PowerCheck(self):
        # TODO
        if not self.COMBO:
            pass

        def CheckFlush():
            pass
        def CheckStraight():
            pass
        def CheckPair():
            pass
        def CheckTPlus():
            pass
        if self.game.STAGE < 2:
            flush = CheckFlush()
            stra = CheckStraight()
            pair = CheckPair()
            tplus = CheckTPlus()
        else:
            pass
        power = int(random.random() * 100)
        return power
    
    def ChooseOpponent(self):
        opponent = random.choice(self.game.PLAYERS)
        if opponent.NAME == self.NAME:
            opponent = self.ChooseOpponent()
        return opponent

    def Decide(self):
        if self.IS_AI:
            self.logger.debug(f'{self} 行动')
            self.logger.debug(f'{self.NAME}手牌：{self.HAND}')
            if not self.CASH:
                if self.game.STAGE > 1:
                    self.logger.info(f'{self.NAME}无筹码，跳过此轮')
                else:
                    q = random.random()
                    if q > 0.5:
                        self.BuyIn()
                    else:
                        self.Bye()
            else:
                self.logger.info(f'{self.NAME}正在决策...')
                s = random.random() + 1
                time.sleep(s)
                self.logger.debug(f'{self.NAME}现金 ${self.CASH}，当前由{self.game.LASTBETPLAYER}下注 ${self.game.LASTBET}')

                power = self.PowerCheck() #TODO
                self.logger.debug(f'Player.PowerCheck() => {power}')

                if self.LASTBET == self.game.LASTBET:
                    pass
                else:
                    if self.CASH <= self.game.LASTBET:
                        q = random.random()
                        if q > 0.5:                        
                            self.Talk('allin')
                        else:
                            self.Talk('fold')
                    elif power < 20:
                        self.Talk('fold')
                    elif 20 <= power < 40:
                        if not self.game.LASTBET:
                            self.Talk('check')
                        else:
                            self.Talk('fold')
                    elif 40 <= power < 60:
                        q = random.random()
                        if not self.game.LASTBET:
                            if q > 0.5:
                                self.Talk('raise')
                            else:
                                self.Talk('check')
                        else:
                            if q > 0.5:
                                self.Talk('raise')
                            else:
                                self.Talk('call')
                    elif 60 <= power < 90:
                        self.Talk('raise')
                    elif power >= 90:
                        self.Talk('allin')
            input('Press ENTER to continue...\n')
        else:
            if self.game.OVER:
                if not self.CASH:
                    options = ['BUY IN', 'GAME OVER']
                    menu = TerminalMenu(options)
                    decision = menu.show()
                    decision = options[decision]
                    if decision == 'BUY IN':
                        self.BuyIn()
                    else:
                        self.game.Exit()
            else:
                print(f'{self.game.LASTBETPLAYER}刚才下注 {self.game.LASTBET}')
                print(f'当前底池: ${self.game.POOL}')
                print(f'你的手牌：{self.HAND}')
                if self.game.STAGE >= 2:
                    print(f'桌面：{self.game.TABLE}')
                    print(f'你的牌力：{self.COMBO}')

                rate = None
                if self.CASH:
                    rate = self.game.Pool/self.CASH
                    if rate:
                        print(f'你的筹码：${self.CASH}，底池筹码比{rate:.2%}')
                    else:
                        print(f'你的筹码：${self.CASH}')
                    options = self.Options()
                    menu = TerminalMenu(options)
                    decision = menu.show()
                    decision = options[decision]
                    self.logger.debug(f'user input: {decision}')
                    self.Talk(decision)
                else:
                    print(f'你已经 all in 了，看戏吧')
                    input('Press ENTER to continue...\n')

    def Options(self):
        # options = ['allin','call','check','fold','raise',]
        options = []
        if self.game.LASTBET >= self.CASH:
            options = ['allin', 'fold']
        else:
            if self.game.STAGE == 0:
                if self.NAME == self.game.SBPLAYER.NAME:
                    options = ['call','check','fold']
                else:
                    options = ['call','raise','allin','fold',]
            else:
                if not self.game.LASTBET:
                    options = ['call','check','raise','allin','fold',]
                else:
                    options = ['call','raise','allin','fold',]

        self.logger.debug(f'options: {options}')
        return options

    def Check(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Check')
        self.game.LASTBET = 0
    
    def Call(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Call')
        bet = self.game.LASTBET
        self.logger.debug(f'{self.NAME}准备跟注 ${bet}')
        self.Bet(bet)

    def Raise(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Raise')
        bet  = self.game.SB * (int(random.random()*4) + 1) + self.game.LASTBET
        if bet >= self.CASH:
            self.Talk('allin')
        else:
            self.game.LASTBET = bet
            self.logger.debug(f'{self.NAME}准备加注 ${bet}')
            self.Bet(bet)

    def AllIn(self):
        self.logger.debug(f'[Player] {self.NAME} [action] AllIn')
        bet = self.CASH
        self.logger.debug(f'{self.NAME}准备全下 ${bet}')
        self.Bet(bet)
        self.game.LASTBET = bet

    def Fold(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Fold')
        pop = self.game.PLAYERS.pop(self.INDEX)
        try:
            assert pop is self
        except:
            raise PlayerIndexError()
        left = '、'.join([p.NAME for p in self.game.PLAYERS])
        print(f'{self.NAME}离开牌桌，还剩{left}')
        self.game.OFFTABLE.append(pop)
        #self.logger.debug(f'game.PLAYERS = {game.PLAYERS}')

    def BuyIn(self):
        self.logger.debug(f'[Player] {self.NAME} [action] BuyIn')
        try:
            try:
                self.game.POSITIONS.Add(self)
            except GameAlreadyFullError:
                print(f'目前没有空余座位！')
        except:
            raise BuyInError()
        else:
            self.CASH += self.game.BUYIN
            self.ONTABLE = True
            self.BUYINTIMES += 1
            self.logger.info(f'{self.NAME} 买入 ${self.game.BUYIN}，上桌')
            self.Talk('buyin')
    
    def Bye(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Bye')
        self.game.PLAYERS.pop(self.INDEX)
        self.game.ONTABLE.remove(self)
        self.logger.info(f'{self.NAME} 下桌了')
        self.game.WORLD.add(self)
        self.Talk('bye')
