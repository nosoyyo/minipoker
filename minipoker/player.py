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
from minipoker.utils import GetSeed


class Player():

    STATES = ['ACTIVE','DEACTIVE','FOLD']
    FACES = '๐๐๐๐๐๐๐๐คฃ๐๐๐๐๐๐๐ฅฐ๐๐๐๐๐๐๐๐๐คช๐คจ๐ง๐ค๐๐คฉ๐ฅณ๐๐๐๐๐๐๐๐ฃ๐๐ซ๐ฉ\
๐ฅบ๐ข๐ญ๐ค๐ ๐ก๐คฌ๐คฏ๐ณ๐ฅต๐ฅถ๐ฑ๐จ๐ฐ๐ฅ๐๐ค๐ค๐คญ๐คซ๐คฅ๐ถ๐๐๐ฌ๐๐ฏ๐ฆ๐ง๐ฎ๐ฒ๐ฅฑ๐ด๐คค๐ช๐ต๐ค๐ฅด๐คข๐คฎ๐คง๐ท๐ค๐ค๐ค๐ค ๐๐ฟ๐น๐บ๐คก๐ฉ๐ป๐๐ฝ๐ค๐๐บ๐ธ๐น๐ป\
๐ผ๐ฝ๐๐ฟ๐พ'

    # sample personalities here
    PERSONALITIES = ['conservative','normal','progressive']
    
    def __init__(self, game, name=None, is_AI=True,) -> None:
        self.logger = logging.getLogger('main.Player')

        self.game = game

        if not name:
            name = 'arslan'
        self.NAME = name

        self.CORPUS = Corpus(self)

        self.IS_AI = is_AI
        self.PERSONALITY = random.choice(self.PERSONALITIES)
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

        # transitions
        self.m = Machine(model=self, states=self.STATES, initial='DEACTIVE')
        self.m.add_transition(trigger='_active', source='*', dest='ACTIVE')
        self.m.add_transition(trigger='_deactive', source='*', dest='DEACTIVE')
        self.m.add_transition(trigger='_fold', source='*', dest='FOLD')

    def __repr__(self) -> str:
        info = f'<{self.NAME} ๆป็ไบ${self.WEALTH} ็ญน็ ${self.CASH}>'
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
            err = f'{self.NAME}ไธ่ฝไธๆณจ ${bet}๏ผ็ญน็ ๅชๅฉ ${self.CASH}'
            self.logger.fatal(err)
            raise OverBetError(err)
        # max valid bet
        elif bet >= self.game.LASTBET:
            money = [p.CASH + p.LASTBET for p in self.game.PLAYERS if p is not self]
            if bet >= max(money):
                self.logger.debug(f'max money ${max(money)}')
                bet = max(money) - self.LASTBET
                self.logger.info(f'ๆๅคๅฏไธๆณจ ${bet}')
                self._bet(bet)
            else:
                self._bet(bet)
        else:
            self._bet(bet)
    
    def _bet(self, bet):
        bet = int(bet)
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
            word = f'{word}๏ผๆข่ทๅ{opponent.NAME}'
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
        
        content = f'{self.NAME}๏ผ[bold green]{word}\n'
        self.game.SCREEN.Chat(content)

    def Comment(self, opponent, command):
        #test
        if command == 'allin' and self.Q > 0.6:
            CORPUS = Corpus(self)
            if len(self.game.TABLE.items):
                num = random.choice(self.game.TABLE.items).__str__()[0]
                comment = f'nb๏ผไธๆก{num}ๅ{opponent.NAME}'
            else:
                comment = f'{random.choice(CORPUS.COMMENTALLIN)}{opponent.NAME}'
            
            self.game.SCREEN.Update(f'{self.NAME}๏ผ{comment}', 'chat')

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
        #print(f'basic => {basic}')
        _power += basic

        if self.game._stage < 2:
            c1, c2 = hand.items
            # CheckFlush
            if hand.type[-1] == 's':
                random.seed(GetSeed())
                flush = int(random.random()*20 + 10)
                ##print(f'flush => {flush}')
                _power += flush
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
                #print(f'p1={p1} p2={p2} p3={p3}')
                _power += p1 + p2 + p3
            elif any([c.weight.number > 8 for c in hand.items]):
                #print('any T+ =>')
                tplus = int(max(c1,c2).weight.number * random.random()*10)
                if tplus > 20:
                    tplus = 20
                elif tplus < 0:
                    tplus = 10
                #print(f'tplus => {tplus}')
                if min(c1,c2).weight.number < 7:
                    tminor = int(min(c1,c2).weight.number * random.random()*10)
                    if tminor > 10:
                        tminor = 10
                    #print(f'tminor => {tminor}')
                    _power -= tminor

                _power += tplus
                
        else:
            basic = int(self.COMBO.type * (self.Q + random.random()+1)) * 10
            factor = 1
            # distribute by COMBO.type
            if self.COMBO.type == 1:
                factor = 0.3
            elif self.COMBO.type == 2:
                factor = 0.6
            elif self.COMBO.type == 3:
                factor = 0.9
            elif self.COMBO.type == 4:
                factor = 1.5
            elif self.COMBO.type == 5:
                factor = 2
            elif self.COMBO.type == 6:
                factor = 3.2
            elif self.COMBO.type == 7:
                factor = 4.2
            elif self.COMBO.type == 8:
                factor = 5
            elif self.COMBO.type == 9:
                factor = 10
            basic *= factor
            #print(f'basic *= factor => {basic}')

            #CheckDrawing #TODO
            f = set([c.suit.number for c in  self.COMBO.cards.items])
            if len(f) == 3:
                print(f'drawing: 2 to flush')
                basic += 5
            elif len(f) == 2:
                print(f'drawing: 1 to flush')
                basic += 20
            
            _power += basic

        if _power > 99:
            _power = 99
        elif _power < 1:
            _power = 1
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
        if 0 < power < 10:
            self.Fold()
        elif 10 <= power < 20:
            if not self.game.LASTBET:
                self.Check()
            else:
                self.Fold()
        elif 20 <= power < 66:
            q = random.random()
            if q > 0.3:
                self.Call()
            else:
                if not self.game.LASTBET:
                    self.Check()
                else:
                    self.Fold()
        elif 66 <= power < 80:
            q = random.random()
            if q > 0.3:
                self.Raise()
            else:
                if not self.game.LASTBET:
                    self.Check()
                else:
                    self.Call()
        elif 80 <= power < 90:
            self.Raise()
        elif power >= 90:
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
                info = f'ๅบไบDEBUGไนๅๆณ็ฎ็๏ผไฝ ็็ญน็ ๅขๅ ${self.game.BUYIN}'
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
        # a simple sample here
        factor = 1
        pers = self.PERSONALITY
        if pers == 'conservative':
            factor = 0.7
        elif pers == 'normal':
            if random.random() > 0.5:
                factor = 1.1
            else:
                factor = 0.9
        elif pers == 'progressive':
            factor = 1.3

        return random.random() * factor

    def CountDown(self, limit=10):
        t = int(random.random()*limit + 3)
        if t > limit:
            t = limit
        assert t <= limit
        mins, secs = divmod(t, 60) 
        delta = limit - secs
        while t: 
            timer = f'{secs + delta:02d} {self.NAME}ๆญฃๅจๅณ็ญ...'
            if self.COMBO:
                debug = f'{self.COMBO} => {self._power}'
            else:
                debug = f'{self.HAND} => {self._power}'
            #timer += debug
            self.game.SCREEN.Timer(timer)
            #print(timer, end="\r") 
            s = 0.8 + random.random()/10
            time.sleep(0.9) 
            t -= 1
            delta -= 1

    def Decide(self):
        print(chr(27)+'[2j')
        print('\033c')
        print('\x1bc')
        if self.IS_AI and self.ONTABLE:
            self.game.POOL.Show()
            self.Tech()
            self.logger.debug(f'{self} ่กๅจ')
            self.logger.debug(f'{self.NAME}ๆ็๏ผ{self.HAND}')
            if not self.CASH:
                self.logger.debug(f'{self.NAME}ๆ ็ญน็ ๏ผ่ทณ่ฟๆญค่ฝฎ')
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
                        if q < 0.4: #TODO
                            self.Check()
                        else:
                            self.Raise()
                    elif 81 <= power < 95:
                        self.Raise()
                    elif power >= 95:
                        q = self.Q
                        if q > 0.6:
                            self.AllIn()
                        else:
                            self.Raise()
                    else:
                        self.Check()
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
        else:
            # human player starts deciding from here
            if self.ONTABLE:
                #self.PowerCheck()
                #self.logger.debug(f'game.LASTACTION {self.game.LASTACTION}')
                self.game.POOL.Show()
                self.game.SCREEN.Update(f'ไฝ ็ๆ็๏ผ{self.HAND}', 'title')

                if self.CASH:
                    self.Tech(AI=False)
                    options = self.Options()
                    menu = Menu(options, self.game)
                    decision = menu.Show()
                    self.Action(command=decision)
                elif all([p.ALLIN for p in self.game.PLAYERS]):
                    self.game.SCREEN.Update(f'ไฝ ๅทฒ็ป all in ไบ๏ผ็ๆๅง', 'title')
                else:
                    self.game.SCREEN.Update(f'ไฝ ๅทฒ็ป all in ไบ๏ผ็ๆๅง', 'title')

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

    def Tech(self, AI=True):
        content = ''
        if not AI:
            rate = self.game.POOL.SUM/self.CASH
            if rate:
                content = f'ๅบๆฑ  ${self.game.POOL.SUM}\nๅบๆฑ ็ญน็ ๆฏ{rate:.2%}\n'
                if self.game._stage >= 2:
                    content += (f'ไฝ ็็ๅ\n{self.COMBO}\n')
                    #content += (f'self._power {self._power}\n')
                    content += (f'ๅฝๅๅฌ็ {"#TODO"}\n')
                    content += (f'้ฃ้ฉ {"#TODO"}')
            else:
                content = f'ไฝ ็็ญน็ ๏ผ${self.CASH}'
        else:
            face = random.choice(self.FACES)
            #self.game.SCREEN.Update(self.FACES.index(face),'title')
            content = f'ๅพฎ่กจๆ [{self.NAME}]{face}\nๅบ  ๆฑ  ${self.game.POOL.SUM}\n็ญน  ็  ${self.CASH}'

        self.game.SCREEN.Update(content, 'tech', title='ๆๆฏๅบ')

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
        self.LASTACTION = '่ฟ็'
    
    def Call(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Call')
        self.Talk('call')
        bet = self.game.POOL.CURRENTMAX - self.LASTBET
        self.logger.debug(f'{self.NAME}ๅๅค่ทๆณจ ${bet}')
        self.Bet(bet)
        self.LASTACTION = '่ทๆณจ'

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
            self.logger.debug(f'{self.NAME}ๅๅคๅ ๆณจ ${bet}')
            self.Bet(bet)
            self.LASTACTION = 'ๅ ๆณจ'
            

    def AllIn(self):
        self.logger.debug(f'[Player] {self.NAME} [action] AllIn')
        self.Talk('allin')
        bet = self.CASH
        self.logger.debug(f'{self.NAME}ๅๅคๅจไธ ${bet}')

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
        ontable = 'ใ'.join([p.NAME for p in self.game.PLAYERS])
        self.game.SCREEN.Update(f'{self.NAME}ๅผ็๏ผ็ฉๅฎถ่ฟๅฉ{ontable}', 'title')
        #self.logger.debug(f'game.PLAYERS = {game.PLAYERS}')
        self.LASTACTION = 'ๅผ็'

    def ShowHand(self):
        self.logger.debug(f'[Player] {self.NAME} [action] ShowHand')
        self.logger.info(f'{self} ๆ็ {self.HAND}')
        self.game.SCREEN.Update(f'{self} ๆ็ {self.HAND}\n็ๅ {self.COMBO}', 'tech')

    def BuyIn(self):
        self.logger.debug(f'[Player] {self.NAME} [action] BuyIn')
        self.game.POSITIONS.Add(self)
        self.CASH += self.game.BUYIN
        self.ONTABLE = True
        self.BUYINTIMES += 1
        self.logger.info(f'{self.NAME}ไนฐๅฅ ${self.game.BUYIN} ็ญน็ ๏ผไธๆก')
        self.game.SCREEN.Update(f'{self.NAME}ไนฐๅฅ ${self.game.BUYIN}๏ผไธๆก', 'title')
        self.Talk('buyin')
    
    def Bye(self):
        self.logger.debug(f'[Player] {self.NAME} [action] Bye')
        self.ONTABLE = False
        flag = self.game.POSITIONS.Remove(self)
        self.logger.debug(f'Player.game.POSITIONS.Remove({self}) => {flag}')
        self.logger.info(f'{self.NAME}ไธๆกไบ')
        self.logger.debug(f'self.game.POSITIONS {self.game.POSITIONS}')
        self.logger.debug(f'self.game.PLAYERS {self.game.PLAYERS}')

        if self.IS_AI:
            if self.Q > 0.5: # may vary per personalities later # TODO
                self.BuyIn()
                self.Talk('buyin')
            else:
                self.game.WORLD.Add(self)
                self.game.SCREEN.Title(f'{self.NAME}่พๅๆๆ็ญน็ ๏ผ้ปฏ็ถ็ฆปๅบ๐ข')
                self.Talk('bye')
        else:
            print(f'็ญน็ ่พๅไบ๏ผไนฐๅฅๅ๏ผ')
            options = [f'ไนฐๅฅ ${self.game.BUYIN}', 'ไธไบ๏ผๅฐ่ฟๅง']
            menu = Menu(options, self.game)
            decision = menu.Show()

            if decision == f'ไนฐๅฅ ${self.game.BUYIN}':
                self.BuyIn()
            else:
                self.game.Exit()
