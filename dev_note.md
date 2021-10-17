# HIGHEST PRIORITY
match every player's bet within one round
reactions to one's action

# ISSUE
#ISSUE repeated Player fucking everywhere
#ISSUE all in guy still can all in
#ISSUE every one can call $0 @game.Turn
#ISSUE wrong game.NUMOFGAMES
#ISSUE wrong SB/BB order after NewGame(), should add TABLEPOSITION
#FIXED game.PLAYERS.hand not refreshed after NextGame()
#ISSUE missing action in River stage
#FIXED the 1st player of flop round should be able to check

# TODO
#TODO 上桌机制
#DONE add Player.WEALTH
#TODO real powercheck based on 1~13, T+, TT+ and pocket pair etc.
#TODO end-game summary, actually one more STAGE
#TODO player lost all money should be move into a new list
#TODO manual/auto SB raise
#TODO BB preflop raise

#TODO random smalltalk
#TODO comments on self.hand, game.TABLE and/or other people's hand/action
#TODO real AI: characteristics
#TODO player/AI interact: trashtalk etc.

# IMPROVEMENT
#DONE improve Pool: seperate every bet
#DONE game.SBPLAYER and game.BBPLAYER
#TODO side pool regularization
#TODO game history & stats
#TODO drawing calculation and related stuff(bluffing etc.)
#TODO stuff about nuts: powercheck & talk
#IMPROVE CLI menu: 1/3 pool etc. helper
#IMPROVE game.PLAYERS should be more mechanical

# LONGTERM PLAN
#TODO probability helper/trainer
#TODO go online
#TODO UI
#TODO web UI
#TODO unit tests