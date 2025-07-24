from otree.api import *
from random import randrange
from time import sleep

doc = """
Public goods with punishment 
"""


class C(BaseConstants):
    NAME_IN_URL = 'pgg_ConInfPun'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 5
    ENDOWMENT = cu(9)
    MULTIPLIER = 1.2
    MAX_PUNISHMENT = 12
    PUNISHMENT_SCHEDULE = {
        0: 0,
        1: 0.33,
        2: 0.66,
        3: 1,
        4: 1.32,
        5: 1.65,
        6: 1.98,
        7: 2.31,
        8: 2.64,
        9: 2.97,
        10: 3.3,
        11: 3.63,
        12: 3.96

    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    total_contribution_after_multiplier = models.CurrencyField()
    individual_share = models.CurrencyField()
    implemented_punishment_player_id = models.IntegerField()


class Player(BasePlayer):
    contribution = models.CurrencyField(
       choices=[0, 3, 6, 9], label="Bitte wählen Sie zwischen den Werten 0, 3, 6 und 9 Euro in der Liste aus."
    )
    contribution_received = models.CurrencyField()
    punishment = models.IntegerField(
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], label="Bitte wählen Sie einen Wert zwischen 0 und 12 Punkten aus der Liste aus."
    )
    punishment_received = models.IntegerField()
    payoff_other_player = models.CurrencyField()
    punishment_implemented = models.BooleanField()
    uni_of_other_player = models.StringField
    uni_of_player = models.StringField
    reaktion = models.StringField(
        choices=['Gar nicht zufrieden', 'Nicht zufrieden', 'Weder nicht zufrieden noch zufrieden', 'Zufrieden', 'Sehr zufrieden'],
        label='Wie zufrieden sind Sie mit der eben gespielten Runde?',
        widget=widgets.RadioSelect,
    )
    belief = models.CurrencyField(
        choices=[0, 3, 6, 9],
        label='Wie viel glauben Sie hat das andere Mitglied zum gemeinsamen Projekt beigetragen? Bitte geben Sie eine Schätzung ab. Wenn Ihre Antwort mit '
              'dem tatsächlichen Beitrag des anderen Mitglieds zum gemeinsamen Projekt übereinstimmt, zahlen wir Ihnen zusätzlich <b>0,25 Euro</b>.',
        widget=widgets.RadioSelect,
    )


# FUNCTIONS


def uni_of_player(player: Player):
    if player.session.config['test_mode']:
        uni_id = player.participant.id_in_session % 2
    else:
        uni_id = player.participant.uni
    return 'Kassel' if uni_id == 0 else 'Passau'


# PAGES
class WaitAndGroupPage(WaitPage):

    body_text = "Bitte warten Sie bis die anderen Teilnehmenden bereit sind."

    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        if not subsession.session.config['test_mode']:
            print('grouping people')
            print(f'round number {subsession.round_number}')
            print(subsession.session.groups_per_round[subsession.round_number])
            subsession.set_group_matrix(subsession.session.groups_per_round[subsession.round_number])
            print('Session Code')
            print(subsession.session.code)


class Contribute1(Page):
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player: Player):
        other_player = player.get_others_in_group()[0]
        return dict(uni_of_other_player=uni_of_player(other_player))


class Belief(Page):
    form_model = 'player'
    form_fields = ['belief']


class WaitPage1(WaitPage):
    body_text = "Bitte warten Sie bis die anderen Teilnehmenden bereit sind."
    @staticmethod
    def after_all_players_arrive(group: Group):
        players_in_group = group.get_players()
        group.total_contribution = 0
        for player in players_in_group:
            player.contribution_received = player.get_others_in_group()[0].contribution
            group.total_contribution += player.field_maybe_none('contribution')
            if player.belief == player.contribution_received:
                try:
                    player.participant.beliefs_correctly_guessed = player.participant.beliefs_correctly_guessed + 1
                except KeyError:
                    player.participant.beliefs_correctly_guessed = 1

        group.total_contribution_after_multiplier = group.total_contribution * 1.2

        for player in players_in_group:
            player.payoff = group.total_contribution_after_multiplier / 2 + C.ENDOWMENT - player.contribution
            player.payoff_other_player = group.total_contribution_after_multiplier / 2 + C.ENDOWMENT - player.contribution_received


class Results1(Page):
    @staticmethod
    def vars_for_template(player: Player):
        other_player = player.get_others_in_group()[0]
        player_share = player.group.field_maybe_none('total_contribution_after_multiplier') / 2 if player.group.field_maybe_none('total_contribution_after_multiplier') else 0
        return dict(
            player_share=player_share,
            uni_of_other_player=uni_of_player(other_player),
            uni_of_player=uni_of_player(player)
        )


class Punish(Page):
    form_model = 'player'
    form_fields = ['punishment']

    @staticmethod
    def vars_for_template(player: Player):
        other_player = player.get_others_in_group()[0]
        player_share = player.group.field_maybe_none(
            'total_contribution_after_multiplier') / 2 if player.group.field_maybe_none(
            'total_contribution_after_multiplier') else 0
        return dict(
            player_share=player_share,
            uni_of_other_player=uni_of_player(other_player),
            uni_of_player=uni_of_player(player)
        )


class Reaktion(Page):
    form_model = 'player'
    form_fields = ['reaktion']


class WaitPage2(WaitPage):
    body_text = "Bitte warten Sie bis die anderen Teilnehmenden bereit sind."
    @staticmethod
    def after_all_players_arrive(group: Group):
        implemented_punishment_player_id = randrange(2) + 1
        group.implemented_punishment_player_id = implemented_punishment_player_id

        players_in_group = group.get_players()

        for player in players_in_group:
            player.punishment_received = player.get_others_in_group()[0].punishment

        for player in players_in_group:
            if player.id_in_group == implemented_punishment_player_id:
                player.punishment_implemented = True
                player.payoff = (C.MAX_PUNISHMENT - player.punishment) * 0.33 + player.payoff

            else:
                player.punishment_implemented = False
                player.payoff = player.payoff - player.punishment_received
                player.payoff = player.payoff if player.payoff > 0 else 0



class Results2(Page):
    @staticmethod
    def vars_for_template(player: Player):
        punishes = player.group.implemented_punishment_player_id == player.id_in_group
        other_player = player.get_others_in_group()[0]
        player_payoff_part1 = player.group.total_contribution_after_multiplier / 2 + (C.ENDOWMENT - player.contribution)
        other_player_payoff_part1 = other_player.group.total_contribution_after_multiplier / 2 + (C.ENDOWMENT - other_player.contribution)
        return dict(
            punishes=punishes,
            uni_of_other_player=uni_of_player(other_player),
            uni_of_player=uni_of_player(player),
            punishment_received=player.punishment_received,
            punishment=player.punishment,
            player_payoff_part1=player_payoff_part1,
            other_player_payoff_part1=other_player_payoff_part1,
            other_player_payoff_part2=other_player.payoff
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            random_round = randrange(1, C.NUM_ROUNDS)
            player.participant.selected_round = random_round
            for r in range(1, C.NUM_ROUNDS+1):
                if r != random_round:
                    player.participant.payoff -= player.in_round(r).payoff
                else:
                    player.participant.punishment_pgg_payoff = player.in_round(r).payoff
            try:
                player.payoff += player.session.config['belief_reward'] * player.participant.beliefs_correctly_guessed
            except KeyError:
                pass



page_sequence = [
    WaitAndGroupPage,
    Contribute1,
    Belief,
    WaitPage1,
    Results1,
    Punish,
    WaitPage2,
    Results2,
    Reaktion
]