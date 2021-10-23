import random
import time

from rich import print
from rich.live import Live, Console
from rich.table import Table
from rich.layout import Layout, Panel

from main import __VERSION__


class Screen:

    LAYOUT = Layout()
    LAYOUT.split_column(
        Layout(name='title'),
        Layout(name='table'),
        Layout(name="lower")
        )

    def __init__(self) -> None:
        self.console = Console()
        self._chat = []
        self.title = "[magenta]zhihu special edition"
        self.subtitle = __VERSION__
        
        self.LAYOUT["title"].update(Panel('MINIPOKER', title=self.title, subtitle=self.subtitle))

        self.LAYOUT["lower"].split_row(
        Layout(name="menu"),
        Layout(name="chat"),
        )

        self.LAYOUT["menu"].update(Panel('test', title='MENU', subtitle=None))
        self.LAYOUT["chat"].update(Panel('test', title='CHAT', subtitle='📱'))

        self.LAYOUT['title'].size = 3
        self.LAYOUT['title'].minimum_size = 3
        self.LAYOUT['table'].minimum_size = 12
        #print(self.LAYOUT)
    
    #def __repr__(self):
    #    print(self.LAYOUT)
    #    return '<Screen>'

    def Chat(self, content):
        self._chat.append(content)
        if len(self._chat) > 6:
            self._chat.pop(0)
        lines = ''
        for i in range(len(self._chat)):
            lines += f'{self._chat[i]}\n'
        lines = lines[:-2]
        panel = Panel(lines)
        self.Update(lines, 'chat', '聊天室', '📱')

    def Update(self, content, which, title=None, subtitle=None):
        '''
        :which: `str` ['title', 'table', 'menu', 'chat',]
        '''
        title = title or self.title
        subtitle = subtitle or self.subtitle
        self.LAYOUT[which].update(Panel(content, title=title, subtitle=subtitle))
        print(self.LAYOUT)
