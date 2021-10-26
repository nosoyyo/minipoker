import time
import random
import logging
from rich import print, box
from transitions import Machine
from thpoker.core import Hand, Combo
from rich.table import Table as RichTable

from minipoker.menu import Menu
from minipoker.corpus import Corpus
from minipoker.exceptions import OverBetError, InvalidBetError


class Player():

    STATES = ['ACTIVE','DEACTIVE','FOLD']
    
    def __init__(self, game, name=None, is_AI=True,) -> None:
        self.logger = logging.getLogger('main.Player')

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
        self._total_bet = 0
        #self._power = 0

        # transitions
        self.m = Machine(model=self, states=self.STATES, initial='DEACTIVE')
        self.m.add_transition(trigger='_active', source='*', dest='ACTIVE')
        self.m.add_transition(trigger='_deactive', source='*', dest='DEACTIVE')
        self.m.add_transition(trigger='_fold', source='*', dest='FOLD')

    def __repr__(self) -> str:
        info = f'<{self.NAME} 总盈亏${self.WEALTH} 筹码${self.CASH}>'
        if not self.ONTABLE:
            info = f'[FOLD] {info}'
        elif self.POSITION:
            info = f'[{self.POSITION}] {info}'
        if self.INDEX:
            info = f'[{self.INDEX}] {info}'
        else:
            #dirty hack
            info = f'[0] {info}'
        return info

    @property
    def WEALTH(self):
        return self.CASH - (self.game.BUYIN * self.BUYINTIMES)
    
    @property
    def INDEX(self) -> int:
        try:
            return self.game.PLAYERS.index(self)
        except:
            return None

    @property
    def HAND(self):
        string = '/'.join(self._raw_hand)
        return(Hand(string))

    def Bet(self, bet):
        self.logger.debug(f'bet {bet} self.game.CASHES {self.game.CASHES}')

        if bet < self.game.SB or type(bet) is not int:
            raise InvalidBetError(f'cannot bet ${bet}!')
        elif self.CASH < bet:
            err = f'{self.NAME}不能下注 ${bet}，筹码只剩 ${self.CASH}'
            self.logger.fatal(err)
            raise OverBetError(err)
        # max valid bet
        elif bet >= self.game.LASTBET:
            money = [p.CASH + p.LASTBET for p in self.game.PLAYERS if p is not self]
            if bet >= max(money):
                self.logger.debug(f'max money ${max(money)}')
                bet = max(money) - self.LASTBET
                self.logger.info(f'最多可下注 ${bet}')
                self._bet(bet)
            else:
                self._bet(bet)
        else:
            self._bet(bet)
    
    def _bet(self, bet):
        self.logger.info(f'{self} [Bet] {bet}')
        self.CASH -= bet
        self._total_bet += bet
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
            opponent = self.ChooseOpponent()
            word = f'{trash}{opponent.NAME}'
        elif command == 'buyin':
            CORPUS = Corpus(self)
            word = random.choice(CORPUS.BUYIN)
        elif command == 'bye':
            word = random.choice(self.CORPUS.BYE)
        else:
            word = command
        
        content = f'{self.NAME}：[bold green]{word}\n'
        self.game.SCREEN.Chat(content)

    def Comment(self, opponent, command):
        #test
        if command == 'allin' and self.Q > 0.6:
            CORPUS = Corpus(self)
            if len(self.game.TABLE.items):
                num = random.choice(self.game.TABLE.items).__str__()[0]
                comment = f'nb，三条{num}呗{opponent.NAME}'
            else:
                comment = f'{random.choice(CORPUS.COMMENTALLIN)}{opponent.NAME}'
            
            self.game.SCREEN.Update(f'{self.NAME}：{comment}', 'chat')

    @property
    def COMBO(self) -> Combo:
        return Combo(hand=self.HAND, table=self.game.TABLE)

    @property
    def _power(self):
        return self.PowerCheck()

    def PowerCheck(self) -> int:
        '''
        :return: <int> range(0,100)
        '''
        hand = self.HAND
        _power = 0
        basic = sum([c.weight.number for c in hand.items])
        print(f'basic => {basic}')
        _power += basic

        if self.game._stage < 2:
            c1, c2 = hand.items
            # CheckFlush
            if hand.type[-1] == 's':
                _power += 10
            # CheckStraight
            if abs(c1.weight.number - c2.weight.number) < 5:
                _power += 10
            # CheckPair
            if hand.is_pair:
                _power += 20
            # CheckTPlus
            if all([c.weight.number > 8 for c in hand.items]):
                print('all T+ =>')
                p1 = int((c1.weight.number-8) * random.random()*3)
                p2 =  int((c2.weight.number-8) * random.random()*3)
                p3 = int(sum([c.weight.number*0x3c18/10000 for c in hand.items]))
                print(f'p1={p1} p2={p2} p3={p3}')
                _power += p1 + p2 + p3
            elif any([c.weight.number > 8 for c in hand.items]):
                print('any T+ =>')
                tplus = int(max(c1,c2).weight.number * random.random()*6)
                print(tplus)
                _power += tplus
                
        else:
            #_power = self.COMBO.type * int((self.Q + random.random()) * 10)
            pass

        if _power > 99:
            _power = 99
        #modifier = 0.8
        return _power
    
    def ChooseOpponent(self):
        opponent = random.choice(self.game.PLAYERS)
        if opponent is self:
            opponent = self.ChooseOpponent()
        return opponent

    def Action(self, power=0, command=None):
        '''
        most parameters fine-tuning work here
        '''
        if 0 < power < 12:
            self.Fold()
        elif 12 <= power < 27:
            if not self.game.LASTBET:
                self.Check()
            else:
                self.Fold()
        elif 27 <= power < 66:
            q = random.random()
            if q > 0.4:
                self.Call()
            else:
                if not self.game.LASTBET:
                    self.Check()
                else:
                    self.Fold()
        elif 66 <= power < 88:
            q = random.random()
            if q > 0.6:
                self.Raise()
            else:
                if not self.game.LASTBET:
                    self.Check()
                else:
                    self.Call()
        elif 88 <= power < 95:
            self.Raise()
        elif power >= 95:
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

            #DEBUG
            elif command == ':$cash':
                self.CASH += self.game.BUYIN
                info = f'出于DEBUG之合法目的，你的筹码增加${self.game.BUYIN}'
                self.game.SCREEN.Update(info, 'tech', title='DEBUG')
                self.logger.debug(info)
                self.Decide()
            elif command == ':locals':
                self.logger.debug(f'locals() => {locals()}')
                self.Decide()
            elif command == ':status':
                #TODO
                self.game.SCREEN.Table(self.game.STATUS, 'DEBUG')
                self.Decide()

    @property
    def Q(self):
        '''
        #TODO different personalities return various Q types
        '''
        return random.random()

    def CountDown(self, limit=10):
        t = int(random.random()*limit + 3)
        if t > limit:
            t = limit
        assert t <= limit
        mins, secs = divmod(t, 60) 
        delta = limit - secs
        while t: 
            timer = f'{secs + delta:02d} {self.NAME}正在决策...'
            debug = f'{self.HAND} => {self._power}'
            timer += debug
            self.game.SCREEN.Timer(timer)
            #print(timer, end="\r") 
            s = 0.8 + random.random()/10
            time.sleep(0.9) 
            t -= 1
            delta -= 1

    def Decide(self):
        if self.IS_AI and self.ONTABLE:
            self.PowerCheck()
            self.logger.debug(f'{self} 行动')
            self.logger.debug(f'{self.NAME}手牌：{self.HAND}')
            if not self.CASH:
                self.logger.debug(f'{self.NAME}无筹码，跳过此轮')
            else:
                self.CountDown()
                self.logger.debug(f'game.LASTACTION {self.game.LASTACTION}')

                power = self._power
                self.logger.debug(f'Player.PowerCheck() => {power}')

                lb = self.LASTBET
                cmx = self.game.POOL.CURRENTMAX
                glb = self.game.LASTBET
                self.logger.debug(f'Player.game.POOL.CURRENTMAX {cmx}')
                self.logger.debug(f'Player.LASTBET {lb}')
                self.logger.debug(f'game.LASTBET {glb}')
                if not cmx:
                    # here is when self is 1st player to act
                    # options: check, raise, allin, fold
                    if 46 <= power < 81:
                        # avoid `call` because nothing to call currently
                        q = self.Q
                        if q < 0.5:
                            self.Check()
                        else:
                            self.Raise()
                    else:
                        self.Check()
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
            self.game.POOL.Show()
            #input('\n\n\nPress ENTER to continue...\n')
        else:
            # human player starts deciding from here
            if self.ONTABLE:
                self.PowerCheck()
                #self.logger.debug(f'game.LASTACTION {self.game.LASTACTION}')
                self.game.POOL.Show()
                self.game.SCREEN.Update(f'你的手牌：{self.HAND}', 'title')

                if self.CASH:
                    self.Tech()
                    options = self.Options()
                    menu = Menu(options, self.game)
                    decision = menu.Show()
                    self.Action(command=decision)
                elif all([p.ALLIN for p in self.game.PLAYERS]):
                    self.game.SCREEN.Update(f'你已经 all in 了，看戏吧', 'title')
                else:
                    self.game.SCREEN.Update(f'你已经 all in 了，看戏吧', 'title')

    def Options(self):
        # options = ['allin','call','check','fold','raise']
        options = []
        if self.game.POOL.CURRENTMAX >= self.CASH:
            options = ['allin', 'fold',]
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

    def Tech(self):
        rate = self.game.POOL.SUM/self.CASH
        if rate:
            content = f'当前下注 {self.game.POOL.CURRENTMAX}\n\
底池 ${self.game.POOL.SUM}\n底池筹码比{rate:.2%}\n'
            if self.game._stage >= 2:
                content += (f'你的牌力\n{self.COMBO}\n')
                content += (f'self._power {self._power}\n')
                content += (f'当前听牌 {"#TODO"}\n')
                content += (f'风险 {"#TODO"}')
        else:
            content = f'你的筹码：${self.CASH}'
        self.game.SCREEN.Update(content, 'tech', title='技术区')

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
        #if bet < self.game.POOL.CURRENTMAX:
        #    self.SIDEPOOL = self.game.POOL.SidePool(self, bet)

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
        self._fold() # for FSM
        ontable = '、'.join([p.NAME for p in self.game.PLAYERS])
        self.game.SCREEN.Update(f'{self.NAME}弃牌，玩家还剩{ontable}', 'title')
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
        self.game.SCREEN.Update(f'{self.NAME}买入 ${self.game.BUYIN}，上桌', 'title')
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
            if self.Q > 0.6: # may vary per personalities later # TODO
                self.BuyIn()
            else:
                self.game.WORLD.Add(self)
                self.game.SCREEN.Title(f'{self.NAME}输光所有筹码，黯然离场😢')
                self.Talk('bye')
        else:
            print(f'筹码输光了，买入吗？')
            options = [f'买入 ${self.game.BUYIN}', '不了，到这吧']
            menu = Menu(options, self.game)
            decision = menu.Show()

            if decision == f'买入 ${self.game.BUYIN}':
                self.BuyIn()
            else:
                self.game.Exit()
