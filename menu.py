from rich.table import Table
from pynput.keyboard import Key, Listener


class Menu:

    def __init__(self, options: list, p) -> None:
        self.OPTIONS = options
        self._choice = 0
        self.SCREEN = p.game.SCREEN
        self._t = Table(show_edge=False,show_header=False,show_lines=False)

        for i in range(len(self.OPTIONS)):
            self._t.add_row(self.OPTIONS[i])
            #self._t.rows[i].active = False
            self._t.row_styles.append('dim')

        self._t.row_styles[0] = 'reverse blink'
        

    def Show(self):
        

        def Dim():
            for i in range(len(self._t.rows)):
                self._t.row_styles[i] = 'dim'
            self.SCREEN.Update(self._t, 'menu')

        def Refresh(i=0):
            Dim()
            self._t.row_styles[i] = 'reverse blink'
            self.SCREEN.Update(self._t, 'menu')

        Refresh(self._choice)

        def on_press(key):

            if key == Key.space:
                Dim()
                return False
            elif key == Key.up:
                if self._choice == 0:
                    self._choice = len(self._t.rows) - 1
                else:
                    self._choice -= 1
            elif key == Key.down:
                if self._choice == len(self._t.rows) - 1:
                    self._choice = 0
                else:
                    self._choice += 1
            
            Refresh(self._choice)

        with Listener(on_press=on_press) as listener:
            listener.join()
            return self.OPTIONS[self._choice]