from rich.table import Table
from pynput.keyboard import Key, Listener, GlobalHotKeys


class Menu:

    DEBUG = [{'DEBUG':[':$cash',':locals',':status',]}]

    def __init__(self, options: list, game, which='menu') -> None:
        self.game = game
        self.TITLE = 'MENU'
        self.SUBTITLE = None
        self.OPTIONS = options
        self._debug()
        self._choice = 0
        self._prev = None
        self.SCREEN = game.SCREEN
        self._t = Table(
            show_edge=False,
            show_header=False,
            show_lines=False,
            )
        self._t.add_column(justify='middle')
        #self._t.padding = (10,10,10,10)

        for i in range(len(self.OPTIONS)):
            if type(self.OPTIONS[i]) is not dict:
                self._t.add_row(self.OPTIONS[i])
                # here just a practically blank style, e.g. `frame` 
            else:
                self._t.add_row([k for k in self.OPTIONS[i]][0])
            self._t.row_styles.append('frame')

        self._t.row_styles[0] = 'reverse blink'

    def _debug(self):
        if self.DEBUG[0] not in self.OPTIONS:
            self.OPTIONS += self.DEBUG

    def Show(self, options=None, which='menu'):
        '''
        :which: to decide which area of the Layout to show this menu 
        '''
        options = options or self.OPTIONS

        def Dim():
            for i in range(len(self._t.rows)):
                self._t.row_styles[i] = 'dim'
            self.SCREEN.Update(self._t, which, title=self.TITLE, subtitle=self.SUBTITLE)

        def Refresh(i=0):
            Dim()
            self._t.row_styles[i] = 'reverse blink'
            self.SCREEN.Update(self._t, which, title=self.TITLE, subtitle=self.SUBTITLE)

        Refresh(self._choice)

        def kill(r):
            listener.stop()
            return r

        def on_press(key, options=options):

            if key == Key.space or key == Key.enter:
                Dim()
                if type(self.OPTIONS[self._choice]) is not dict:
                    listener.stop()
                    # this will kill the menu
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
            elif key == Key.left:
                if self._prev:
                    self._prev.Show()
            elif key == Key.right:
                if type(self.OPTIONS[self._choice]) is dict:
                    options = [v for v in self.OPTIONS[self._choice].values()][0]
                    menu = Menu(options, self.game)
                    menu._prev = self
                    menu.Show()
                else:
                    pass
            
            Refresh(self._choice)

        with Listener(on_press=on_press) as listener:
            # .join() for blocking, .start() for non-blocking
            try:
                self.listener = listener
                listener.join()
                decision = self.OPTIONS[self._choice]
            finally:
                listener.stop()

            if type(decision) is not dict:
                return decision
            else:
                decision = [v for v in self.OPTIONS[self._choice].values()][0][self._choice]
                return decision
