import time
import random
import logging
from thpoker.core import Hand, Combo
from simple_term_menu import TerminalMenu

from exceptions import OverBetError
from utils import CORPUS, ShowHand


class Player():
    def __init__(self, cash, name=None, is_AI=True,) -> None:
        self.logger = logging.getLogger('main.player')

        if not name:
            name = 'arslan'
        self.name = name
        self.is_AI = is_AI
        self.hand = []
        self.cash = cash
        self.index = None

    def __repr__(self) -> str:
        return f'<{self.name} ${self.cash}>'
    
    def GetSelfIndex(self, game) -> int:
        for i in range(len(game.PLAYERS)):
            if self.name == game.PLAYERS[i].name:
                return i

    def ShowHand(self) -> Hand:
        string = ''
        for i in range(len(self.hand)):
            string += self.hand[i] + '/'
        return(Hand(string))

    def Bet(self, bet, game):
        if self.cash < bet:
            raise OverBetError(f'{self.name}不能下注 ${bet}，筹码只剩 ${self.cash} 了')
        else:
            self.cash -= bet
            game.POOL.Add(self, game, bet)
            game.LASTBETPLAYER = self
        return game.POOL

    def Talk(self, game, command, p=None):
        time.sleep(0.3)
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
            opponent = self.ChooseOpponent(game)
            word = f'{word}，跟吗{opponent.name}'
            self.Raise(game)
        elif command == 'allin':
            word = random.choice(CORPUS['ALLIN'])
            self.AllIn(game)
        elif command == 'trash':
            trash = random.choice(CORPUS['TRASHTALK'])
            word = f'{trash}{p.name}'
        elif command == 'buyin':
            word = random.choice(CORPUS['BUYIN'])
        elif command == 'bye':
            word = random.choice(CORPUS['BYE'])
        else:
            word = command
        print(f'{self.name}：{word}\n')

    def Combo(self, game) -> Combo:
        self.combo = Combo(hand=self.ShowHand(), table=ShowHand(game.TABLE))
        self.logger.debug(f'{self.name}的combo：{self.combo}')
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
            self.logger.debug(f'{self.name}行动')
            if not self.cash:
                if game.STAGE > 1:
                    self.logger.info(f'{self.name}无筹码，跳过此轮')
                else:
                    q = random.random()
                    if q > 0.5:
                        self.BuyIn()
                    else:
                        self.Bye()
            else:
                print(f'{self.name}正在决策...')
                s = random.random()
                time.sleep(s)
                self.logger.debug(f'time.sleep: {s}')

                power = self.PowerCheck() #TODO
                self.logger.debug(f'power: {power}')

                if self.cash <= game.LASTBET:
                    q = random.random()
                    self.logger.debug(f'{self.name}现金 ${self.cash}，当前下注 ${game.LASTBET}')
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
            if game.OVER:
                if not self.cash:
                    options = ['BUY IN', 'GAME OVER']
                    menu = TerminalMenu(options)
                    decision = menu.show()
                    decision = options[decision]
                    if decision == 'BUY IN':
                        self.BuyIn()
                    else:
                        game.Exit()
            else:
                print(f'{game.LASTBETPLAYER}刚才下注 {game.LASTBET}')
                print(f'当前底池: ${game.POOL}')
                print(f'你的筹码：${self.cash}，底池筹码比{game.Pool/self.cash:.2%}')
                print(f'你的手牌：{ShowHand(self.hand)}')
                if game.STAGE >= 2:
                    print(f'桌面：{ShowHand(game.TABLE)}')
                    print(f'你的牌力：{self.combo}')
                options = self.Options(game)
                menu = TerminalMenu(options)
                decision = menu.show()
                decision = options[decision]
                self.logger.info(f'you choose: {decision}')
                self.Talk(game, decision)

    def Options(self, game):
        # options = ['allin','call','check','fold','raise',]
        options = []
        if game.LASTBET >= self.cash:
            options = ['allin', 'fold']
        else:
            if game.STAGE == 0:
                if self.name == game.SBPLAYER.name:
                    options = ['call','check','fold']
                else:
                    options = ['call','raise','allin','fold',]
            else:
                if not game.LASTBET:
                    options = ['call','check','raise','allin','fold',]
                else:
                    options = ['call','raise','allin','fold',]

        self.logger.debug(f'options: {options}')
        return options

    def Check(self, game):
        self.logger.debug(f'[Player] {self.name} [action] Check')
        game.LASTBET = 0
    
    def Call(self, game):
        self.logger.debug(f'[Player] {self.name} [action] Call')
        bet = game.LASTBET
        self.logger.debug(f'{self.name}准备跟注 ${bet}')
        self.Bet(bet, game)

    def Raise(self, game):
        self.logger.debug(f'[Player] {self.name} [action] Raise')
        bet  = game.SB * (int(random.random()*4) + 1) + game.LASTBET
        if bet >= self.cash:
            self.Talk(game, 'allin')
        else:
            game.LASTBET = bet
            self.logger.debug(f'{self.name}准备加注 ${bet}')
            self.Bet(bet, game)

    def AllIn(self, game):
        self.logger.debug(f'[Player] {self.name} [action] AllIn')
        bet = self.cash
        self.logger.debug(f'{self.name}准备全下 ${bet}')
        self.Bet(bet, game)
        game.LASTBET = bet

    def Fold(self, game):
        self.logger.debug(f'[Player] {self.name} [action] Fold')
        index = self.GetSelfIndex(game)
        game.PLAYERS.pop(index)
        self.logger.debug(f'Player.Fold cause game.PLAYERS.pop({index})')
        left = '、'.join([p.name for p in game.PLAYERS])
        print(f'{self.name}离开牌桌，还剩{left}')
        game.WAITLIST.append(self)
        #self.logger.debug(f'game.PLAYERS = {game.PLAYERS}')

    def BuyIn(self, game):
        self.logger.debug(f'[Player] {self.name} [action] BuyIn')
        self.cash += game.BUYIN
        self.logger.info(f'{self.name} 买入 ${game.BUYIN}，上桌')
        self.Talk(game, 'buyin')
    
    def Bye(self, game):
        self.logger.debug(f'[Player] {self.name} [action] Bye')
        index = self.GetSelfIndex(game)
        game.PLAYERS.pop(index)
        self.logger.info(f'{self.name} 下桌了')
        self.Talk('bye')
