import logging

class Pool:

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
        logger = logging.getLogger('game.Pool.Add')
        self.pools[index][p.INDEX] += bet

    def EVEN(self, index=0):
        flag = False
        if len(set(self.pools[index])) == 1:
            flag = True
        return flag

    def Give(self, p, index=0) -> None:
        p.CASH += sum(self.pools[index])
        # here we do no clean, will do Pool.__init__ later in NewGame()

    def Side(self, bet: int, index) -> None:
        #TODO
        pass