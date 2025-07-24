from otree.api import *



doc = """
This application provides a webpage instructing participants how to get paid.
Examples are given for the lab and Amazon Mechanical Turk (AMT).
"""


class C(BaseConstants):
    NAME_IN_URL = 'payment_info'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    paypal = models.StringField()

    prior_experiment_participation = models.IntegerField(
        label="Wie oft haben Sie zuvor schon an ähnlichen Experimenten teilgenommen? Eine ungefähre Schätzung genügt.",
        min=0, max=100
    )

    prior_economics_participation = models.StringField(
        label='Haben Sie schon einmal eine Lehrveranstaltung mit Inhalten aus der Spieltheorie oder der'
              ' Verhaltensökonomik belegt?', choices=['Ja', 'Nein'],
        widget=widgets.RadioSelect)


# FUNCTIONS
# PAGES
class PaymentInfo(Page):
    form_model = 'player'
    form_fields = ['paypal']

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        beliefs_payoff = cu(0)
        try:
            beliefs_payoff = cu(player.session.config['belief_reward'] * participant.beliefs_correctly_guessed)
        except KeyError:
            pass
        return dict(redemption_code=participant.label or participant.code, beliefs_payoff=beliefs_payoff)



class ExPost(Page):
    form_model = 'player'
    form_fields = ['prior_experiment_participation', 'prior_economics_participation']


class Ende(Page):
    pass


page_sequence = [ExPost, PaymentInfo, Ende]
