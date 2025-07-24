from otree.api import *

doc = """
Simple version of comprehension test
"""


class C(BaseConstants):
    NAME_IN_URL = 'comprehension_test_simple'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)
    quiz1 = models.StringField(label='Richtig oder falsch? Die Gruppe besteht aus zwei Mitgliedern, wobei die '
                                     'Zusammensetzung der Gruppe zufällig gebildet wird.',
                               choices=['Richtig', 'Falsch'],
                               widget=widgets.RadioSelect)

    quiz2 = models.StringField(label="Angenommen Sie haben 4 Euro zum gemeinsamen Projekt beigetragen, und das andere "
                                     "Mitglied hat ebenfalls 4 Euro zum gemeinsamen Projekt beigetragen. Wäre Ihr "
                                     "Gewinn höher, niedriger oder gleich, wenn das andere Mitglied mehr als 4 Euro "
                                     "beigetragen hätte? (Tipp: Es wären dann mehr Euro im gemeinsamen Projekt.)",
                               choices=['Höher', 'Niedriger', 'Gleich'],
                               widget=widgets.RadioSelect)
    quiz3 = models.StringField(label="Angenommen Sie haben 3 Euro zum gemeinsamen Projekt beigetragen, und das andere "
                                     "Mitglied hat ebenfalls 3 Euro zum gemeinsamen Projekt beigetragen. Wäre Ihr"
                                     " Gewinn höher, niedriger oder gleich, wenn Sie mehr als 3 Euro beigetragen hätten?"
                                     " (Tipp: Sie würden weniger Euro behalten, und es wären mehr Euro im gemeinsamen "
                                     "Projekt. Überlegen Sie, welcher Effekt stärker ist.)",
                               choices=['Höher', 'Niedriger', 'Gleich'],
                               widget=widgets.RadioSelect)
    quiz4 = models.StringField(label='Angenommen Sie haben 5 Euro zum gemeinsamen Projekt beigetragen und das andere '
                                      'Mitglied hat 3 Euro zum gemeinsamen Projekt beigetragen.'
                                      ' Was ist Ihr Gewinn in Euro?',
                                choices=['2,00', '4,80', '8,80', '9,20', '10,50'],
                                widget=widgets.RadioSelect)




# PAGES
class Questions(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4']

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(quiz1='Richtig', quiz2='Höher', quiz3='Niedriger', quiz4='8,80')
        solutions1 = dict(quiz1='Erklärung: Diese Aussage ist richtig.',
                          quiz2='Erklärung: Ihr Gewinn wäre höher, wenn das andere Mitglied mehr beigetragen hätte.'
                                  ' Sie würden mehr Euro aus dem gemeinsamen Projekt erhalten.',
                          quiz3='Erklärung: Ihr Gewinn wäre niedriger, wenn Sie mehr beigetragen hätten. Sie würden '
                                  'weniger Euro behalten, und dies überwiegt den Effekt von mehr Euro'
                                  ' im gemeinsamen Projekt.',
                          quiz4='Erklärung: Ihr Gewinn beträgt 8,80 Euro (= 4 + 1,2*(5+3) / 2).')



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
            player.participant.control_questions_payoff = cu(0.5)
        else:
            player.participant.control_questions_payoff = cu(0)



class Instructions1(Page):
    pass


class Ende(Page):
    pass


page_sequence = [Instructions1, Questions, Ende]