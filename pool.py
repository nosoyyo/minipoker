import logging
from rich.table import Table
from rich.console import Console

from exceptions import InvalidBetError


logger = logging.getLogger('game.Pool')
console = Console()


class Pool():

    def __init__(self, game) -> None:
        self.game = game
        pool = {}
        for p in self.game.ALLPLAYERS:
            pool.update({p : 0})
        self.pools = [pool]

        self.CURRENT = {}
        for p in self.game.ALLPLAYERS:
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
    def MAXTOTALBET(self):
        result = []
        tb = [p._total_bet for p in self.game.ALLPLAYERS]
        for p in self.game.ALLPLAYERS:
            if p._total_bet == max(tb):
                result.append(p)
        return result

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
        #return self.CURRENTSUM + sum(self.pools[0].values())
        _sum = sum(p._total_bet for p in self.game.ALLPLAYERS)
        assert _sum == self.CURRENTSUM + sum(self.pools[0].values())
        return _sum

    def Account(self):
        '''
        account at and only at the end of each round.
        create side-pool when necessary.
        for end-game accounting, see game.Summary()

        side-pool: when an all-in player can't match a previously bet
        '''
        # normally
        for k in self.CURRENT.keys():
            if self.CURRENT[k]:
                v = self.pools[0][k] + self.CURRENT[k]
                self.pools[0][k] = v
                # dont forget clear `CURRENT`
                self.CURRENT[k] = 0

        # end-game accounting
        if len(self.game.WINNERS) == 1:
            if self.game.WINNERS[0]._total_bet < self.MAXTOTALBET:
                self.SidePool('single')
            else:
                self.game.WINNERS[0].CASH += self.SUM
        elif len(self.game.WINNERS) >= 1:
            self.SidePool('multi')

    def Show(self):
        t = f'\n第 {self.game.NUMOFGAMES} 局 {self.game.STAGE}\n'
        st = '等待发牌...'
        if len(self.game.TABLE.items):
            st = f'{self.game.TABLE}'
        table = Table()
        table.add_column("位置", justify="right", style="cyan", no_wrap=True)
        table.add_column("玩家", justify="right", style="cyan", no_wrap=True)
        #table.add_column("总盈亏", style="blue")
        table.add_column("筹码", style="magenta")
        table.add_column("当前下注", justify="right", style="green")
        table.add_column("总下注", justify="right", style="green")
        table.add_column("状态", justify="middle", style="white")

        c = self.CURRENT
        for p in c:
            if p.state == 'FOLD':
                pos = f'[dim]{p.POSITION}'
                name = f'[dim]{p.NAME}'
            elif p.state != 'ACTIVE':
                pos = p.POSITION
                name = p.NAME
            else:
                pos = f'[reverse]{p.POSITION}'
                name = f'[reverse]{p.NAME}'

            table.add_row(pos,
                          name,
                          #str(p.WEALTH),
                          str(p.CASH),
                          str(self.CURRENT[p]),
                          str(self.pools[0][p]),
                          p.LASTACTION)

        self.game.SCREEN.Update(table, 'table', title=t, subtitle=st)


    def SidePool(self, condition) -> None:
        # so it's time to divide self.SUM
        _sum = self.SUM
        if condition == 'single':
            # after accounted this single winner
            # there still could be more players dividing the rest stake
            WINNER = self.WINNERS[0]
            prize = 0
            for p in self.game.ALLPLAYERS:
                if p._total_bet > WINNER._total_bet:
                    self.game.logger.debug(f'SidePool breakpoint #0 {locals()}')
                    prize += WINNER._total_bet
                    p._total_bet -= WINNER._total_bet
                    _sum -= WINNER._total_bet
                else:
                    self.game.logger.debug(f'SidePool breakpoint #1 {locals()}')
                    prize += p._total_bet
                    p._total_bet = 0
                    _sum -= p._total_bet
            WINNER.cash += prize
            if _sum - prize:
                #assert sum([p._total_bet for p in positions]) == (sum - prize)
                if self.SUM == (sum - prize):
                    self.game.logger.debug(f'SidePool breakpoint #2 {locals()}')
                    for p in self.game.ALLPLAYERS:
                        p.CASH += p._total_bet
                else:
                    # if not the situation above, decide new winners and recursion
                    ps = self.PLAYERS
                    # take your money and get lost
                    ps.remove(WINNER)
                    # decide new winner
                    WINNERS = self.game.Elect(ps)
                    self.game.logger.debug(f'SidePool breakpoint #3 {locals()}')
                    if len(WINNERS) == 1:
                        self.SidePool('single')
                    else:
                        self.SidePool('multi')

        elif condition == 'multi':
            # simplest situation
            if len(set([p._total_bet for p in self.game.WINNERS])) == 1:
                self.game.logger.debug(f'SidePool breakpoint #4 {locals()}')
                share = self.SUM / len(self.game.WINNERS)
                for p in self.game.WINNERS:
                    p.CASH += share
            else:
                pass
