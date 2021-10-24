from transitions import Machine


from game import Game
from player import Player

game = Game()


class PlayerMachine:

    STATES = ['BUYIN','SB','BB','GOOD','CHECK','CALL','RAISE','ALLIN','FOLD','BYE',]

    def __init__(self):
        self.m = Machine(states=self.STATES, initial='BUYIN')
        # transitions
        self.m = Machine(model=self, states=self.STATES, initial='BUYIN')
        self.m.add_transition(trigger='Decide', source='*', dest='GOOD')
        self.m.add_transition(trigger='Check', source='*', dest='CHECK')
        self.m.add_transition(trigger='Call', source='*', dest='CALL')
        self.m.add_transition(trigger='Raise', source='*', dest='RAISE')
        self.m.add_transition(trigger='AllIn', source='*', dest='ALLIN')
        self.m.add_transition(trigger='Fold', source='*', dest='FOLD')
        self.m.add_transition(trigger='Bye', source='*', dest='BYE')

    def Decide(self):
        print(f'im deciding...')
    def Call(self):
        print(f'im calling...')
    def Fold(self):
        print(f'im folding...')


class GameMachina:
    
    STATES = ['INIT','BLIND','PREFLOP','FLOP','TURN','RIVER','OVER']

    def __init__(self):
        self.machine = Machine(model=self, states=self.STAGES, initial='INIT')
        self.machine.add_ordered_transitions(loop=True)

        self.machine.add_transition(trigger='Over', source='*', dest='OVER')


