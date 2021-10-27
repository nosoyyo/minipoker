__AUTHOR__ = "arslan"
__EMAIL__ = "oyyoson@gmail.com"
__COPYRIGHT__ = "Copyright © 2021 MSFC Studios. All rights reserved."
__LICENSE__ = "MIT"
__VERSION_INFO__ = (0, 0, -1, 'α')
__VERSION__ = ".".join(map(str, __VERSION_INFO__))

import sys
import termios
import logging
from rich.traceback import install
install(show_locals=True)
from rich.logging import RichHandler

from minipoker.game import Game
from minipoker.splash import Splash

logging.basicConfig(
    level="WARNING",
    format="'[%(levelname)s] %(asctime)s@%(name)s.%(funcName)s:\n%(message)s'",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)


#FORMAT = logging.Formatter('[%(levelname)s] %(asctime)s@%(name)s.%(funcName)s:\n%(message)s')
logger = logging.getLogger('main')
#rh = RichHandler()
#sh = logging.StreamHandler()
#sh.setFormatter(FORMAT)
#logger.addHandler(sh)
#fh.setFormatter(FORMAT)
fh = logging.FileHandler('main.log')
logger.addHandler(fh)


import sys
import os

if os.name == 'nt':
    import msvcrt
    import ctypes

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]

def hide_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def main(name, world):
    # 获取标准输入的描述符
    fd = sys.stdin.fileno()

    # 获取标准输入(终端)的设置
    old_ttyinfo = termios.tcgetattr(fd)

    # 配置终端
    new_ttyinfo = old_ttyinfo[:]

    # 使用非规范模式(索引3是c_lflag 也就是本地模式)
    new_ttyinfo[3] &= ~termios.ICANON

    # 关闭回显(输入不会被显示)
    new_ttyinfo[3] &= ~termios.ECHO

    # 使设置生效
    termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)

    # 隐藏光标
    hide_cursor()

    game = Game(name=name, world=world)
    game.Start()

    # 回到之前设置
    termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)

    # 显示光标
    show_cursor()

if __name__ == '__main__':
    main()
