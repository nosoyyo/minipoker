import random

from thpoker.core import Hand, Table, Combo, Cards

from utils import DEBUG, RawCards

class Player():
    def __init__(self, name=None, AI=True) -> None:
        if not name:
            name = 'arslan'
        self.name = name
        self.AI = AI
        self.hand = []
        self.cash = 600

    def __repr__(self) -> str:
        return f'<玩家：{self.name}>'

    def Draw(self):
        global DEBUG
        self.hand.append(RawCards.pop())
        self.hand.append(RawCards.pop())
        self.Combo()
        if DEBUG:
            print(f'{self.name}的手牌：{self.ShowHand()}')
    
    def ShowHand(self) -> Hand:
        string = ''
        for i in range(len(self.hand)):
            string += self.hand[i] + '/'
        return(Hand(string))

    def Bet(self, bet, POOL) -> Pool:
        if self.cash < bet:
            raise OverBetError(f'不能下这些，你只有{self.cash}了')
        else:
            self.cash -= bet
            POOL.Add(self.name, bet)
        return POOL

    def Talk(self, command):
        pass

    def Combo(self) -> Combo:
        global TABLE
        global DEBUG
        self.combo = Combo(hand=self.ShowHand(), table=ShowHand(TABLE))
        if DEBUG:
            print(f'{self.name}的combo：{self.combo}')
        return self.combo

    def PowerCheck(self):
        pass
        # flush check
        # ace check

def MakeUpPlayers(num: int=5):
    '''
    :TODO: randomly decide who is SB/BB/...
    0 - SB
    1 - BB
    2 - UTG
    3 - UTG + 1
    4 - CO
    5 - BT
    '''
    global PLAYERS
    PLAYERS = []
    AI_NAMES = ['云师','jimmy仔','修师','范师','西米','铁锤','Zakk','胡哥','六爷','莎翁',]
    random.shuffle(AI_NAMES)
    result = AI_NAMES[:num]
    result = list(map(lambda x: Player(name=x), result))
    result.append(PLAYER)
    random.shuffle(result)
    PLAYERS = result
    return PLAYERS