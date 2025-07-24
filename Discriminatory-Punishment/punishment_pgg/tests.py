from . import *
from random import randrange


class PlayerBot(Bot):
    def play_round(self):
        yield Contribute, dict(contribution=randrange(4))
        yield Results1
        yield Punish, dict(punishment=randrange(6))
        yield Results2
