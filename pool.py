import logging
from rich.table import Table
from rich.console import Console

from exceptions import InvalidBetError


logger = logging.getLogger('game.Pool.Add')
console = Console()


class Pool():

    def __init__(self, game) -> None:
        self.game = game
        players = [i for i in game.POSITIONS.__dict__.values() if i]
        pool = {}
        for p in players:
            pool.update({p : 0})
        self.pools = [pool]

        self.CURRENT = {}
        for p in players:
            self.CURRENT.update({ p : 0 })

    def __repr__(self):
        return f'${self.SUM}'

    def __len__(self) -> int:
        return len(self.pools)

    def Add(self, p, bet):
        '''
        pools[0] is always the main pool, mzmkb;
        '''
        if bet < self.game.SB or type(bet) is not int:
            raise InvalidBetError(f'cannot bet ${bet}!')
        else:
            if p in self.CURRENT.keys():
                bet += self.CURRENT[p]
                self.CURRENT.update({p:bet})
                self.__dict__[p] = bet

    @property
    def CURRENTMAX(self):
        sequence = [v for v in self.CURRENT.values() if v] or [0]
        return max(sequence)

    @property
    def CURRENTANY(self):
        return any([v for v in self.CURRENT.values() if v])
    
    @property
    def CURRENTSUM(self):
        return sum([v for v in self.CURRENT.values() if v])

    @property
    def SUM(self):
        return self.CURRENTSUM + sum(self.pools[0].values())

    def Account(self):
        '''
        account at and only at the end of each round.
        create side-pool when necessary.
        for end-game accounting, see game.Summary()

        side-pool: when an all-in player can't match a previously bet
        '''
        for k in self.CURRENT.keys():
            if self.CURRENT[k]:
                v = self.pools[0][k] + self.CURRENT[k]
                self.pools[0][k] = v
                # dont forget clear `CURRENT`
                self.CURRENT[k] = 0

        if self.game.WINNER:
            self.game.WINNER.CASH += self.SUM

    def Show(self):
        t = f'\n第 {self.game.NUMOFGAMES} 局 {self.game.STAGE}\n'
        if self.game.TABLE:
            t = f't{self.game.TABLE}'
        table = Table(title=t)
        table.add_column("玩家", justify="right", style="cyan", no_wrap=True)
        table.add_column("总盈亏", style="blue")
        table.add_column("筹码", style="magenta")
        table.add_column("本局下注", justify="right", style="green")
        table.add_column("行动", justify="middle", style="white")

        for p in self.pools[0]:
            table.add_row(p.NAME, str(p.WEALTH), str(p.CASH), str(self.pools[0][p]), p.LASTACTION)
        console.print(table)

    def ShowCurrent(self):
        t = f'\n第 {self.game.NUMOFGAMES} 局 {self.game.STAGE}\n'
        if self.game.TABLE:
            t = f't{self.game.TABLE}'
        table = Table(title=f'\n第 {self.game.NUMOFGAMES} 局 {self.game.STAGE}\n')
        table.add_column("玩家", justify="right", style="cyan", no_wrap=True)
        table.add_column("筹码", style="magenta")
        table.add_column("本轮下注", justify="right", style="green")
        table.add_column("行动", justify="middle", style="white")

        c = self.CURRENT
        for p in c:
            if p.state != 'ACTIVE':
                table.add_row(p.NAME, str(p.CASH), str(self.CURRENT[p]), p.LASTACTION)
            else:
                table.add_row(f'[reverse]{p.NAME}', str(p.CASH), str(self.CURRENT[p]), p.LASTACTION)
        console.print(table)

    def SidePool(self, p, bet) -> None:
        pass
