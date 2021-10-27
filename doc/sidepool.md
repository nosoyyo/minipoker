# Side-pool distribution

player  A   B   C   D
bet     100 200 800 800

_sum 1900

when winenr is A:
prize_A = 0
for A, prize_A += 100 => prize_A = 100, _sum == 1800, A._total_bet == 0 
for B, prize_A += 100 => prize_A = 200, _sum == 1700, B._total_bet == 100
for C, prize_A += 100 => prize_A = 300, _sum == 1600, C._total_bet == 700
for D, prize_A += 100 => prize_A = 400, _sum == 1500, D._total_bet == 700

now left B/C/D, let's say B wins:
prize_B = 0
*#no need to kick A out of the loop because A._total_bet = 0 now*
for B, prize_B += B._total_bet => prize_B == 100, _sum == 1400, B._total_bet == 0
for C, prize_B += 200 => prize_B == 300, _sum == 1200, C._total_bet == 500
for D, prize_B += 200 => prize_B == 500, _sum == 1000, D._total_bet == 500

now pool.SUM == 1000, C & D get their $500 back each√

## semi-pseudo code here

```
prize = 0
for p in players:
    if p._total_bet > winner._total_bet:
        prize += winner._total_bet
        p._total_bet -= winner._total_bet
        _sum -= winner._total_bet
    else:
        prize += p._total_bet
        p._total_bet = 0
        _sum -= p._total_bet

winner.cash += prize

if sum - prize:
    assert sum[p._total_bet for p in all_players_no_matter_fold_or_not] == (sum - prize)
    for p in players:
        # get one's money left back
        p.cash += p._total_bet
```