import os
import time
import random

from rich import print
from rich.live import Live, Console
from rich.table import Table
from rich.layout import Layout, Panel

#from minipoker.main import __VERSION__
__VERSION__ = '0.0.1α'


class Screen:

    LAYOUT = Layout()
    LAYOUT.split_column(
        Layout(name='title'),
        Layout(name='table'),
        Layout(name="lower")
        )

    def __init__(self) -> None:
        os.system("clear")
        self.console = Console()
        self._chat = []
        self.title = 'MINIPOKER'
        self.subtitle = "[red]BLV GZ"

        # init title       
        self.LAYOUT['title'].size = 3
        self.LAYOUT['title'].minimum_size = 3
        self.LAYOUT["title"].update(Panel('MINIPOKER', title=self.title, subtitle=self.subtitle))

        # init table
        self.LAYOUT['table'].minimum_size = 12

        # init lower
        self.LAYOUT["lower"].split_row(
        Layout(name="menu"),
        Layout(name="tech"),
        Layout(name="chat"),
        )

        self.LAYOUT["menu"].update(Panel('test', title='MENU', subtitle=None))
        self.LAYOUT["tech"].update(Panel('test', title='技术区', subtitle=None))
        self.LAYOUT["chat"].update(Panel('test', title='CHAT', subtitle='📱'))
    
#        with Live(
#                self.LAYOUT,
#                refresh_per_second=4,
#                screen=True,
#                transient=True,
#                ) as live:
#            #for _ in range(40):
#            time.sleep(0.4)
#            os.system("clear")
#            live.update(self.LAYOUT)

    def Title(self, content, title='MINIPOKER', subtitle=None):
        self.Update(content, 'title', title, subtitle)

    def Table(self, content, title='TABLE', subtitle=None):
        self.Update(content, 'table', title, subtitle)

    def Menu(self, content, title='MENU', subtitle=None):
        self.Update(content, 'menu', title, subtitle)

    def Chat(self, content, title='聊天室', subtitle='📱'):
        self._chat.append(content)
        if len(self._chat) > 6:
            self._chat.pop(0)
        lines = ''
        for i in range(len(self._chat)):
            lines += f'{self._chat[i]}\n'
        lines = lines[:-2]
        #panel = Panel(lines)
        self.Update(lines, 'chat', title, subtitle)

    def Timer(self, timer: str):
        self.Update(timer, 'title')

    def Update(self, content, which, title=None, subtitle=None):
        '''
        :which: `str` ['title', 'table', 'menu', 'chat',]
        '''
        os.system("clear")
        title = title or self.title
        subtitle = subtitle or self.subtitle
        self.LAYOUT[which].update(Panel(content, title=title, subtitle=subtitle))
        print(self.LAYOUT)
