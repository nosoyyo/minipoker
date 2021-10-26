from minipoker.screen import Screen
from minipoker.game import Game


class MockScreen(Screen):

    def __init__(self) -> None:
        self.Chat = self.Update

    def Update(self, s, which=None, title=None, subtitle=None):
        print(f's {s} which {which}')


class MockGame(Game):
    SCREEN = MockScreen()

