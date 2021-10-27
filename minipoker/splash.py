import os
from rich import print
from rich.table import Table
from rich.live import Console
from rich.layout import Layout, Panel

from minipoker.menu import Menu


class Splash():

    def name(self):
        os.system("clear")
        print('\n'*11)
        name = input('                              你的名字：')
        return name

class ScreenWrapper:

    def __init__(self, screen):
        self.SCREEN = screen


class WorldSelector:

    LAYOUT = Layout()
    LAYOUT.split_column(
        Layout(name='title'),
        Layout(name='main'),
        )

    def __init__(self, name=None) -> None:
        os.system("clear")
        self.console = Console()
        self._chat = []
        self.title = 'MINIPOKER'
        self.subtitle = "[red]BLV GZ"
        self.name = name or 'arslan'

        # init title       
        self.LAYOUT['title'].size = 8
        _t = Table(
            show_edge=False,
            show_header=False,
            show_lines=False,
            )
        _t.add_row(f'\n\n\n\n')
        _t.add_row(str.center(f'{self.name}，你好。\n', 72))
        _t.add_row(str.center(f'选择你要前往的世界:', 72))
        self.LAYOUT["title"].update(_t)

        # init main       
        self.LAYOUT['main'].size = 15
        self.LAYOUT['main'].minimum_size = 15
        #self.LAYOUT["main"].update(Panel('MINIPOKER', title=self.title, subtitle=self.subtitle))

    def Update(self, content, which='main', title=None, subtitle=None):
        '''
        :which: `str` ['title', 'table', 'menu', 'chat',]
        '''
        os.system("clear")
        self.LAYOUT['main'].update(content)
        print(self.LAYOUT)

    def menu(self):
        options = ['知乎老友','陌生人和怪咖','必立弗','企业家','足球','影人','rockstar']
        wrapper = ScreenWrapper(self)
        menu = Menu(options, wrapper)
        choice = menu.Show(which='main')
        return choice
