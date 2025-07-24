from otree.api import *

doc = """
Simple version of comprehension test
"""


class C(BaseConstants):
    NAME_IN_URL = 'control_questions_1_ConInfPun'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)
    quiz1 = models.StringField(label='Richtig oder falsch? Die Gruppe besteht aus zwei Mitgliedern. Die Zusammensetzung '
                                     'der Gruppe ändert sich in jeder Runde, so dass Sie in jeder neuen Runde mit einer'
                                     ' anderen Person spielen, mit der Sie zuvor noch nicht gespielt haben.',
                               choices=['Richtig', 'Falsch'],
                               widget=widgets.RadioSelect)

    quiz2 = models.StringField(label="Richtig oder falsch? Das Spiel besteht aus zwei Stufen. In der ersten Stufe"
                                     " erhalten die beiden Mitglieder jeweils 9 Euro und entscheiden, ob und wie viel "
                                     "sie davon zu einem gemeinsamen Projekt beitragen möchten. In der zweiten Stufe"
                                     " erhalten die beiden Mitglieder jeweils 12 Punkte und entscheiden, ob und wie viel"
                                     " sie davon dem anderen Mitglied zuordnen möchten, um dessen Gewinn"
                                     " zu reduzieren.",
                               choices=['Richtig', 'Falsch'],
                               widget=widgets.RadioSelect)
    quiz3 = models.StringField(label="Richtig oder falsch? Beide Mitglieder der Gruppe entscheiden, ob und wie viele "
                                     "Punkte sie dem anderen Mitglied zuordnen möchten, aber nur die Entscheidung eines"
                                     " zufällig ausgewählten Mitglieds wird implementiert. Zum Zeitpunkt der "
                                     "Entscheidung ist noch offen, wessen Entscheidung implementiert wird.",
                               choices=['Richtig', 'Falsch'],
                               widget=widgets.RadioSelect)
    quiz4_1 = models.StringField(label='a) Wäre der Gewinn des anderen Mitglieds höher, '
                                       'niedriger oder gleich, wenn Sie ihm weniger Punkte zugeordnet hätten?',
                                 choices=['Höher', 'Niedriger', 'Gleich'],
                                 widget=widgets.RadioSelect)
    quiz4_2 = models.StringField(label='b) Wäre Ihr eigener Gewinn höher, niedriger oder gleich,'
                                       ' wenn Sie dem anderen Mitglied weniger Punkte zugeordnet hätten?',
                                 choices=['Höher', 'Niedriger', 'Gleich'],
                                 widget=widgets.RadioSelect)
    quiz5 = models.StringField(label='Angenommen beide Mitglieder haben in der ersten Stufe des Spiels jeweils 3 Euro'
                                     ' behalten und 6 Euro zum gemeinsamen Projekt beigetragen. In der zweiten Stufe '
                                     'des Spiels wird die Entscheidung des anderen Mitglieds ausgewählt und '
                                     'implementiert. Das andere Mitglied hat Ihnen 1 Punkt zugeordnet. Wie viele Euro'
                                     ' erhalten Sie als Gewinn?',
                                 choices=['9,20', '12,50', '14,50', '16,50', '18,50'],
                                 widget=widgets.RadioSelect)


class Instructions2(Page):
    pass


class Questions1(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4_1', 'quiz4_2', 'quiz5']

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(quiz1='Richtig', quiz2='Richtig', quiz3='Richtig', quiz4_1='Höher', quiz4_2='Höher', quiz5='9,20')
        solutions1 = dict(quiz1='Erklärung: Diese Aussage ist richtig.',
                          quiz2='Erklärung: Diese Aussage ist richtig.',
                          quiz3='Erklärung: Diese Aussage ist richtig.',
                          quiz4_1='Erklärung: Der Gewinn des anderen Mitglieds wäre höher, denn es würden weniger Euro abgezogen werden.',
                          quiz4_2='Erklärung: Ihr eigener Gewinn wäre höher, denn Sie würden mehr Punkte behalten, die Sie später in Euro ausbezahlt bekommen.',
                          quiz5='Erklärung: Sie erhalten 9,20 Euro als Gewinn. Sie erhalten aus der ersten Stufe 10,20 Euro (3 + 1,2*(6+6) / 2) und in der zweiten Stufe werden davon 1 Euro abgezogen.')


        errors = {name: 'Falsch' for name in solutions if values[name] != solutions[name]}
        if errors:
            player.num_failed_attempts += 1
        if player.num_failed_attempts == 3:
            player.num_failed_attempts += 1
            return solutions1
        if player.num_failed_attempts > 3:
            player.failed_too_many = True

        else:
            return errors

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.num_failed_attempts == 0:
            player.payoff += 0.5
            player.participant.control_questions_payoff += cu(0.5)


class Ende(Page):
    pass


page_sequence = [Instructions2, Questions1, Ende]