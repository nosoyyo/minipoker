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

from game import Game

logging.basicConfig(
    level="DEBUG",
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


def main():
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

    game = Game()
    game.Start()

    # 回到之前设置
    termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)

if __name__ == '__main__':
    main()
