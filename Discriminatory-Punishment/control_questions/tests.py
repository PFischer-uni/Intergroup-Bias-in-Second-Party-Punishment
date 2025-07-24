from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Questions,  dict(quiz1='Richtig', quiz2='Höher', quiz3='Niedriger', quiz4='8,80')
        yield Ende
