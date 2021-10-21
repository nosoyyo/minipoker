import random
import time

from rich import print
from rich.live import Live
from rich.table import Table
from rich.layout import Layout, Panel

from main import __VERSION__


class Screen:

    LAYOUT = Layout()
    LAYOUT.split_column(
        Layout(name='title'),
        Layout(name="lower")
        )
    
    def __init__(self) -> None:
        self.title = "[magenta]zhihu special edition"
        self.subtitle = __VERSION__
        
        self.LAYOUT["title"].update(Panel('MINIPOKER', title=self.title, subtitle=self.subtitle))

        self.LAYOUT["lower"].split_row(
        Layout(name="left"),
        Layout(name="right"),
        )

        self.LAYOUT['title'].size = 6
        self.LAYOUT['title'].minimum_size = 6
        print(self.LAYOUT)
    
    def __repr__(self):
        print(self.LAYOUT)
        return '<Screen>'

    def Update(self, content, which='left'):
        self.LAYOUT[which].update(Panel(content, title=self.title, subtitle=self.subtitle))
        print(self.LAYOUT)
