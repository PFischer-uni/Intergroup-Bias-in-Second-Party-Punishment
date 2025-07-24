from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'pgg'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    ENDOWMENT = cu(9)
    MULTIPLIER = 1.2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    total_contribution_after_multiplier = models.CurrencyField()


class Player(BasePlayer):
    contribution = models.CurrencyField(
        choices=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), label="Bitte wählen Sie einen Wert zwischen 0 und 9 Euro aus der Liste aus."
    )
    contribution_received = models.CurrencyField()
    payoff_other_player = models.CurrencyField()

# FUNCTIONS


def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = (
        group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    )
    for p in players:
        p.payoff = C.ENDOWMENT - p.contribution + group.individual_share



def session_id(group: Group):
    print('SESSION ID')
    print(group.session.code)


# PAGES
class WaitAndGroupPage(WaitPage):

    body_text = "Bitte warten Sie bis die anderen Teilnehmenden bereit sind."

    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        if not subsession.session.config['test_mode']:
            print('grouping people')
            print(subsession.session.groups_per_round[subsession.round_number])
            subsession.set_group_matrix(subsession.session.groups_per_round[0])
            print('Session Code')
            print(subsession.session.code)

class WaitPage1(WaitPage):

    body_text = "Bitte warten Sie bis die anderen Teilnehmenden bereit sind."

    @staticmethod
    def after_all_players_arrive(group: Group):
        players_in_group = group.get_players()
        group.total_contribution = 0
        for player in players_in_group:
            player.participant.pgg_contribution = player.contribution
            player.contribution_received = player.get_others_in_group()[0].contribution
            player.participant.pgg_contribution_received = player.get_others_in_group()[0].contribution
            group.total_contribution += player.field_maybe_none('contribution')
        group.total_contribution_after_multiplier = group.total_contribution * 1.2

        for player in players_in_group:
            player.payoff = group.total_contribution_after_multiplier / 2 + C.ENDOWMENT - player.contribution
            player.participant.pgg_payoff = group.total_contribution_after_multiplier / 2 + C.ENDOWMENT - player.contribution
            player.payoff_other_player = group.total_contribution_after_multiplier / 2 + C.ENDOWMENT - player.contribution_received
            player.participant.pgg_payoff_other_player = group.total_contribution_after_multiplier / 2 + C.ENDOWMENT - player.contribution_received


class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(uni=player.participant.uni)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    body_text = "Bitte warten. Das Spiel wird in kürze weitergehen."


class Results(Page):
    pass


page_sequence = [WaitAndGroupPage, Contribute, Results, WaitPage1]
