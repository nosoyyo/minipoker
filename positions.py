import random
import logging

from exceptions import *


logger = logging.getLogger('game.Positions.Add')


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
        logger.debug(f'game.POSITIONS.AVAILABLE {self.AVAILABLE}')
        if self.AVAILABLE:
            kl = [k for k in self.__dict__.keys() if not self.__dict__[k]]
            random.shuffle(kl)
            key = kl.pop()
            logger.debug(f'key {key}')
            self.__dict__[key] = p
            p.__dict__[key] = True
            logger.debug(f'game.POSITIONS.__dict__ {self.__dict__}')
        else:
            raise GameAlreadyFullError()

    def Remove(self, p):
        for k in [k for k in self.__dict__.keys()]:
            if k in p.__dict__.keys() and p.__dict__[k]:
                self.__dict__.pop(k)

    @property
    def AVAILABLE(self):
        flag = True
        if all(self.__dict__.values()):
            flag = False
        return flag

    def Rotate(self):
        #clear Player.SB etc.
        for k in self.__dict__.keys():
            p = self.__dict__[k]
            p.__dict__[k] = False

        players = [i for i in self.__dict__.values() if i]
        players.append(players.pop(0))
        self.Clear()
        for i in range(len(players)):
            self.__dict__[list(self.__dict__.keys())[i]] = players[i]
        
        #set Player.SB etc.
        for k in self.__dict__.keys():
            p = self.__dict__[k]
            p.__dict__[k] = True

    def Clear(self):
        for k in list(self.__dict__.keys()):
            self.__dict__[k] = None