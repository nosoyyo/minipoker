import time
import random
import logging
from rich import print
from thpoker.core import Hand, Combo
from simple_term_menu import TerminalMenu

from corpus import Corpus
from exceptions import OverBetError, InvalidBetError


class Player():
    
    def __init__(self, game, name=None, is_AI=True,) -> None:
        self.logger = logging.getLogger('main.player')

        self.game = game

        if not name:
            name = 'arslan'
        self.NAME = name

        self.CORPUS = Corpus(self)

        self.IS_AI = is_AI
        self.POSITION = None
        self.SB = False
        self.BB = False
        self._raw_hand = [] #:List:
        self.CASH = 0
        self.BUYINTIMES = 0
        self.ONTABLE = False
        self.LASTBET = 0
        self.LASTACTION = None
        self.GOOD = False

    def __repr__(self) -> str:
        info = f'<{self.NAME} 总盈亏${self.WEALTH} 筹码${self.CASH}>'
        if not self.ONTABLE:
            info = f'[FOLD] {info}'
        elif self.POSITION:
            info = f'[{self.POSITION}] {info}'
        if self.INDEX:
            info = f'[{self.INDEX}] {info}'
        return info

    @property
    def WEALTH(self):
        return self.CASH - (self.game.BUYIN * self.BUYINTIMES)
    
    @property
    def INDEX(self) -> int:
        #TODO: not in PLAYERS but in POSITIONS
        try:
            players = [v for v in self.game.POSITIONS.__dict__.values()]
            return players.index(self)
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
        if bet < self.game.SB or type(bet) is not int:
            raise InvalidBetError(f'cannot bet ${bet}!')
        elif self.CASH < bet:
            self.logger.fatal(f'{self.NAME}不能下注 ${bet}，筹码只剩 ${self.CASH} 了')
            raise OverBetError()
        else:
            self.logger.info(f'{self} [Bet] {bet}')
            # max valid bet
            cashes = [p.CASH > bet for p in self.game.PLAYERS]
            if any(cashes):
                if bet > max(cashes):
                    bet = max(cashes)
                    self.logger.info(f'最多可下注 ${max(cashes)}')

            self.CASH -= bet
            self.game.POOL.Add(self, bet)
            self.game.LASTACTION = {self:bet}
            self.game.LASTBET = bet
            self.LASTBET += bet
            self.Good()
        return self.game.POOL

    def Talk(self, command, p=None):
        time.sleep(0.3)

        if command == 'fold':
            word = random.choice(self.CORPUS.FOLD)       
        elif command == 'check':
            word = random.choice(self.CORPUS.CHECK)
        elif command == 'call':
            CORPUS = Corpus(self)
            word = random.choice(CORPUS.CALL)
        elif command == 'raise':
            word = random.choice(self.CORPUS.RAISE)
            oindex = self.INDEX + 1
            if oindex > len(self.game.PLAYERS) - 2:
                oindex = 0
            opponent = self.game.PLAYERS[oindex]
            word = f'{word}，敢跟吗{opponent.NAME}'
        elif command == 'allin':
            word = random.choice(self.CORPUS.ALLIN)
        elif command == 'trash':
            trash = random.choice(self.CORPUS.TRASHTALK)
            word = f'{trash}{p.NAME}'
        elif command == 'buyin':
            CORPUS = Corpus(self)
            word = random.choice(CORPUS.BUYIN)
        elif command == 'bye':
            word = random.choice(self.CORPUS.BYE)
        else:
            word = command
        print(f'{self.NAME}：{word}\n')

    def Comment(self, opponent, command):
        #test
        if command == 'allin' and self.Q > 0.6:
            CORPUS = Corpus(self)
            if len(self.game.TABLE.items):
                comment = f'nb，四条{random.choice(self.game.TABLE.items)}呗{opponent.NAME}'
            else:
                comment = f'{random.choice(CORPUS.COMMENTALLIN)}{opponent.NAME}'
            
            print(f'{self.NAME}：{comment}')

    @property
    def COMBO(self) -> Combo:
        return Combo(hand=self.HAND, table=self.game.TABLE)
 
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
        if self.game._stage < 2:
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
        if opponent is self:
            opponent = self.ChooseOpponent()
        return opponent

    def Action(self, power=0, command=None):
        '''
        most parameters fine-tuning work here
        '''
        if 0 < power < 18:
            self.Fold()
        elif 18 <= power < 46:
            if not self.game.LASTBET:
                self.Check()
            else:
                self.Fold()
        elif 46 <= power < 66:
            q = random.random()
            if q > 0.6:
                self.Call()
            else:
                if not self.game.LASTBET:
                    self.Check()
                else:
                    self.Fold()
        elif 66 <= power < 81:
            q = random.random()
            if q > 0.6:
                self.Raise()
            else:
                if not self.game.LASTBET:
                    self.Check()
                else:
                    self.Call()
        elif 81 <= power < 98:
            self.Raise()
        elif power >= 98:
            self.logger.debug(f'power >= 94 => {power}')
            self.AllIn()
        else:
            if command == 'check':
                self.Check()
            elif command == 'call':
                self.Call()
            elif command == 'raise':
                self.Raise()
            elif command == 'allin':
                self.AllIn()
            elif command == 'fold':
                self.Fold()

    @property
    def Q(self):
        '''
        #TODO different personalities return various Q types
        '''
        return random.random()

    def Decide(self):
        if self.IS_AI and self.ONTABLE:
            self.logger.debug(f'{self} 行动')
            self.logger.debug(f'{self.NAME}手牌：{self.HAND}')
            if not self.CASH:
                self.logger.debug(f'{self.NAME}无筹码，跳过此轮')
            else:
                self.logger.info(f'{self.NAME}正在决策...\n')
                self.logger.debug(f'game.LASTACTION {self.game.LASTACTION}')

                power = self.PowerCheck() #TODO
                self.logger.debug(f'Player.PowerCheck() => {power}')

                lb = self.LASTBET
                cmx = self.game.POOL.CURRENTMAX
                glb = self.game.LASTBET
                self.logger.debug(f'Player.game.POOL.CURRENTMAX {cmx}')
                self.logger.debug(f'Player.LASTBET {lb}')
                self.logger.debug(f'game.LASTBET {glb}')
                if not cmx:
                    # here is when self is 1st player to act
                    # options: check, raise, allin, fold(extremly rare)
                    if 46 <= power < 81:
                        # avoid `call` because nothing to call currently
                        q = self.Q
                        if q < 0.5:
                            self.Check()
                        else:
                            self.Raise()
                    #self.Action(power) #should be removed this line
                else:
                    if self.LASTBET == self.game.POOL.CURRENTMAX:
                        self.logger.debug(f'self.LASTBET == self.game.POOL.CURRENTMAX {True}')
                        pass
                    elif self.CASH <= self.game.POOL.CURRENTMAX:
                        self.logger.debug(f'self.CASH <= self.game.POOL.CURRENTMAX {True}')
                        #TODO: q would be generated from personality
                        q = random.random()
                        if q > 0.99:
                            # it's 1%, not a small rate!
                            self.AllIn()
                        else:
                            self.Fold()
                    else:
                        self.Action(power)
            s = random.random() + 0.4
            time.sleep(s)
            self.game.POOL.ShowCurrent()
            input('\n\n\nPress ENTER to continue...\n')
        else:
            if self.ONTABLE:
                self.logger.info(f'game.LASTACTION {self.game.LASTACTION}')
                self.game.POOL.ShowCurrent()
                print(f'你的手牌：{self.HAND}')
                if self.game._stage >= 2:
                    print(f'当前桌面 {self.game.TABLE}')
                    print(f'你的牌力 {self.COMBO}')
                    print(f'当前听牌 {"#TODO"}')

                rate = None
                if self.CASH:
                    rate = self.game.POOL.SUM/self.CASH
                    if rate:
                        print(f'你的筹码 ${self.CASH}，当前下注 {self.game.POOL.CURRENTMAX}\n\
底池 ${self.game.POOL.SUM}，底池底池筹码比{rate:.2%}')
                    else:
                        print(f'你的筹码：${self.CASH}')
                    options = self.Options()
                    menu = TerminalMenu(options)
                    decision = menu.show()
                    decision = options[decision]
                    self.logger.debug(f'user input: {decision}')
                    self.Action(command=decision)
                else:
                    print(f'你已经 all in 了，看戏吧')
                    input('Press ENTER to continue...\n')

    def Options(self):
        # options = ['allin','call','check','fold','raise',]
        options = []
        if self.game.POOL.CURRENTMAX >= self.CASH:
            options = ['allin', 'fold']
        else:
            if self.game._stage == 0:
                if self.SB:
                    options = ['call','check','fold']
                else:
                    options = ['call','raise','allin','fold',]
            else:
                if not self.game.LASTBET:
                    options = ['check','raise','allin','fold',]
                else:
                    options = ['call','raise','allin','fold',]

        self.logger.debug(f'options: {options}')
        return options

    def Good(self):
        self.GOOD = True
        for p in self.game.PLAYERS:
            # tricky here
            if p is not self and p.LASTBET != self.game.POOL.CURRENTMAX and not p.ALLIN:
                p.GOOD = False

    def Check(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Check')
        self.Talk('check')
        self.game.LASTBET = 0
        self.Good()
        self.LASTACTION = '过牌'
    
    def Call(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Call')
        self.Talk('call')
        bet = self.game.POOL.CURRENTMAX - self.LASTBET
        self.logger.debug(f'{self.NAME}准备跟注 ${bet}')
        self.Bet(bet)
        self.LASTACTION = '跟注'

    def Raise(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Raise')
        # q should mostly be 2~5
        q = int(random.random()*3) * int(random.random()*2) + 2
        factor = self.game.LASTBET or self.game.BB
        bet  = q * factor - self.LASTBET
        if bet >= self.CASH:
            self.AllIn()
        else:
            self.Talk('raise')
            self.logger.debug(f'{self.NAME}准备加注 ${bet}')
            self.Bet(bet)
            self.LASTACTION = '加注'
            

    def AllIn(self):
        self.logger.debug(f'[Player] {self.NAME} [action] AllIn')
        self.Talk('allin')
        bet = self.CASH
        self.logger.debug(f'{self.NAME}准备全下 ${bet}')

        # create side pool if necessary
        if bet < self.game.POOL.CURRENTMAX:
            self.SIDEPOOL = self.game.POOL.SidePool(self, bet)

        self.Bet(bet)
        self.LASTACTION = 'All In'

        #test, seems not bad so far
        for p in self.game.PLAYERS:
            if p is not self:
                p.Comment(self, 'allin')
    
    @property
    def ALLIN(self):
        flag = False
        if self.ONTABLE and not self.CASH:
            flag = True
        return flag

    def Fold(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Fold')
        self.Talk('fold')
        self.ONTABLE = False
        ontable = '、'.join([p.NAME for p in self.game.PLAYERS])
        print(f'{self.NAME}弃牌，玩家还剩{ontable}')
        #self.logger.debug(f'game.PLAYERS = {game.PLAYERS}')
        self.LASTACTION = '弃牌'

    def ShowHand(self):
        self.logger.debug(f'[Player] {self.NAME} [action] ShowHand')
        self.logger.info(f'{self} 手牌 {self.HAND}')

    def BuyIn(self):
        self.logger.debug(f'[Player] {self.NAME} [action] BuyIn')
        self.game.POSITIONS.Add(self)
        self.CASH += self.game.BUYIN
        self.ONTABLE = True
        self.BUYINTIMES += 1
        self.logger.info(f'{self.NAME}买入 ${self.game.BUYIN} 筹码，上桌')
        self.Talk('buyin')
    
    def Bye(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Bye')
        self.ONTABLE = False
        flag = self.game.POSITIONS.Remove(self)
        self.logger.debug(f'Player.game.POSITIONS.Remove({self}) => {flag}')
        self.logger.info(f'{self.NAME}下桌了')
        self.logger.debug(f'self.game.POSITIONS {self.game.POSITIONS}')
        self.logger.debug(f'self.game.PLAYERS {self.game.PLAYERS}')

        if self.IS_AI:
            self.game.WORLD.Add(self)
            self.Talk('bye')
        else:
            print(f'筹码输光了，买入吗？')
            options = ['对', '不了，到这吧']
            menu = TerminalMenu(options)
            decision = menu.show()
            decision = options[decision]
            print(decision)
            if decision == '对':
                self.BuyIn()
            else:
                self.game.Exit()
