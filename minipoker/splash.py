from rich import print
from rich.live import Live, Console
from rich.table import Table
from rich.layout import Layout, Panel


class Splash():

    def name(self):
        import os
        os.system("clear")
        print('\n'*11)
        name = input('                              你的名字：')
        return name

