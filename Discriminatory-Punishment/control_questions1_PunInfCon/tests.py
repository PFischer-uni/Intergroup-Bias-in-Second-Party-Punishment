from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Instructions
        yield Questions,  dict(quiz1='Richtig', quiz2='Richtig', quiz3='Richtig', quiz4_1='Höher', quiz4_2='Höher', quiz5='2,40')
        yield Ende
