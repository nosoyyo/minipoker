import logging

from exceptions import InvalidBetError


logger = logging.getLogger('game.Pool.Add')


class Pool():

    def __init__(self, game) -> None:
        players = [i for i in game.POSITIONS.__dict__.values() if i]
        pool = {}
        for p in players:
            pool.update({p : 0})
        self.pools = [pool]

        self.CURRENT = {}

    def __repr__(self):
        repr = 'self.pools.__str__()'
        if self.CURRENT:
            repr = f'本轮下注 {self.CURRENT} {repr}'
        return repr

    def Add(self, p, bet):
        '''
        pools[0] is always the main pool, mzmkb;
        '''
        if bet <= 0 or type(bet) is not int:
            raise InvalidBetError(f'cannot bet ${bet}!')
        if p in self.CURRENT.keys():
            bet += self.CURRENT[p]
        self.CURRENT.update({p:bet})

    def Account(self):
        '''
        account at and only at the end of each round.
        create side-pool when necessary.
        for end-game accounting, see game.Summary()

        side-pool: when an all-in player can't match a previously bet
        '''
        self.pools[0].update(self.CURRENT)

class _Pool:

    def __init__(self, n_players) -> None:
        self.pools = [[0]]
        self.pools = [[i for i in self.pools[0] for j in range(n_players)]]
    
    def __len__(self) -> int:
        return len(self.pools)
    
    def __repr__(self) -> str:
        #TODO
        s = sum(self.pools[0])
        return f'${s}: {self.pools}'

    def Add(self, p, bet: int, index=0) -> None:
        self.pools[index][p.INDEX] += bet
        logger.debug(self.pools)

    def EVEN(self, index=0):
        flag = False
        if len(set(self.pools[index])) == 1:
            flag = True
        return flag

    @property    
    def MAX(self):
        m = []
        for pl in self.pools:
            m.append(max(pl))
        return max(m)

    def Give(self, p, index=0) -> None:
        p.CASH += sum(self.pools[index])
        # here we do no clean, will do Pool.__init__ later in NewGame()

    def Side(self, bet: int, index) -> None:
        #TODO
        pass