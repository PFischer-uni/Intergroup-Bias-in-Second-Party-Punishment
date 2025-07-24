from otree.api import Currency as c, currency_range, expect, Bot
from . import *
from random import randrange


class PlayerBot(Bot):
    def play_round(self):
        yield Contribute, dict(contribution=randrange(10))
