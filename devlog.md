# HIGHEST PRIORITY

#ISSUE a `Player` `Call` himself after just `Check`

#ISSUE `Player` didn't disappear from `game.POSITIONS` after `Player.Bye`, neither his status didn't get refreshed. could be something wrong with `Player.AllIn`

#ISSUE a total mess of `game.PLAYERS` or `game.POSITIONS` after 2nd `NewGame`

#ISSUE repeated cards in `Player.HAND` and `game.TABLE`

#ISSUE when two `Player` left @`Flop`, they all folded and 

#ISSUE `Player` need to `Decide` in each round if they could

#ISSUE `Player` need to `ShowHand` when win a p2p All-in situation

#DONE put `POOL.Account` somewhere between `NewRound` or `Action`

#FIXED repeated cards in `Player.HAND` and `game.TABLE`

## rewrite game logic

#FIXED `Player` can only bet a max valid bet no matter how much `CASH` he's got

#FIXED infinite loop @Preflop when bets are even`

#FIXED should call `Summary()` before `Flop` when there's only 1P left

#FIXED offtable player need to get on when `NewGame()`

#DONE add `Positions.Remove`

#DONE adjust `Player.Bye`

## `Pool`

#TODO change `Pool` from list to dict, match `Player` and his `LASTBET

#TODO `Player.Fold` holds a status in `POOL.pools[]`, not `0`

## accounting

#ISSUE match every player's bet within one round

#ISSUE wrong accounting when `game.OVER`

# ISSUE

#ISSUE SB should be able to `Fold`, not to be forced to align BB

#FIXED `Raise` should be more than `BB`

#FIXED repeated `Player` everywhere

#FIXED all in guy still can all in

#FIXED every one can call $0 @`game.Turn`

#FIXED wrong `game.NUMOFGAMES`

#FIXED wrong SB/BB order after `NewGame()`, should add `POSITIONS`

#FIXED `game.PLAYERS.hand` not refreshed after `NextGame()`

#FIXED missing action in `River` stage

#FIXED the 1st player of flop round should be able to `Check`

# TODO

#TODO real `PowerCheck` based on 1~13, T+, TT+ and pocket pair etc.

#TODO end-game `Summary`, actually one more `STAGE`

#TODO side pool regularization

#TODO player lost all money should be move into a new list

#TODO manual/auto SB raise

#TODO BB preflop raise

## AI

### INTERACTIONS

#TODO random `Smalltalk`

#TODO comments on `self.HAND`, `game.TABLE` and/or other people's hand/action

#TODO player/AI interact: `Trashtalk` etc.

### PERSONALITIES

#TODO real AI: characteristics

## DONE

#DONE add `Player.POSITION`

#DONE add `class Positions`

#DONE add `Player.WEALTH`

# IMPROVEMENT

#TODO add certain `People` inherit `class Player` with `People.Hello()` and stuff

#TODO emoji faces beside `game.POOL.Show`, let's call it `MOOD`😎

#TODO too many raise and counter raise @`Preflop`

#TODO reactions to one's action

#DONE improve Pool: seperate every bet

#DONE [deprecated]game.SBPLAYER and game.BBPLAYER

#TODO game history & stats

#TODO drawing calculation and related stuff(bluffing etc.)

#TODO stuff about nuts: powercheck & talk

#IMPROVE CLI menu: 1/3 pool etc. helper

#IMPROVE `game.PLAYERS` should be more mechanical

# LONGTERM PLAN

#TODO probability helper/trainer

#TODO automatic game for like 100,000 games

#TODO go online

#TODO UI

#TODO web UI

#TODO unit tests
