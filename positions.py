import random
import logging

from exceptions import *


class Positions():

    def __init__(self, n=6):
        self.SB = None
        self.BB = None
        self.UTG = None
        self.UTG1 = None
        self.CO = None
        self.BTN = None

    def __len__(self):
        return len(list(self.__dict__.keys()))
    
    def __repr__(self):
        return self.__dict__.__str__()

    def Add(self, p):
        logger = logging.getLogger('game.Positions.Add')
        logger.debug(f'game.POSITIONS.AVAILABLE {self.AVAILABLE}')
        if self.AVAILABLE:
            key = random.choice(list(self.__dict__.keys()))
            logger.debug(f'key {key}')
            self.__dict__[key] = p
            logger.debug(f'game.POSITIONS.__dict__ {self.__dict__}')
        else:
            raise GameAlreadyFullError()

    @property
    def AVAILABLE(self):
        flag = True
        if all(self.__dict__.values()):
            flag = False
        return flag

    def Rotate(self):
        #self.BB = self.SB
        players = [i for i in self.__dict__.values() if i]
        players.append(players.pop(0))
        self.Clear()
        for i in range(len(players)):
            self.__dict__[list(self.__dict__.keys())[i]]= players[i]

    def Clear(self):
        for k in list(self.__dict__.keys()):
            self.__dict__[k] = None