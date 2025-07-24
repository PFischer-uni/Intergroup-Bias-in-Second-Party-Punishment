from os import environ


SESSION_CONFIGS = [
    dict(
        name='ConInfPun',
        display_name="ConInfPun",
        app_sequence=['survey', 'control_questions', 'pgg', 'control_questions1_ConInfPun',
                      'punishment_pgg', 'payment_info'],
        num_demo_participants=2,
        # use_browser_bots=True
    ),

    dict(
        name='PunInfCon',
        display_name="PunInfCon",
        app_sequence=['survey', 'control_questions', 'pgg', 'control_questions1_PunInfCon',
                      'punishment_pgg_PunInfCon', 'payment_info'],
        num_demo_participants=2,
        # use_browser_bots=True
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

# Adding a session config field as a constant for all the games
# punishment_pgg_total_rounds Number of rounds of for the punishment_pgg game,
# it MUST match NUM_ROUNDS in punishment_pgg. Unfortunately no way to ensure this other than manual...

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    punishment_pgg_total_rounds=6,
    belief_reward=0.25,
    test_mode=False,
    doc=""
)

# Adding 3 additional fields to participants across the whole session
# uni (enum) represents which University they come from: 0 (Kassel), 1 (Passau)

# sequence (enum) represents the sequence in which they will play the game
# 0: corresponds to the ConInfPun Sequence (Treatment 1 & Treatment 5)
# 1: corresponds to the ConPunInf Sequence (Treatment 2 & Treatment 6)
# 2: corresponds to the PunConInf Sequence (Treatment 3 & Treatment 7)
# 3: corresponds to the PunInfCon Sequence (Treatment 4 & Treatment 8)

# group_type (enum) corresponds to whether they are in a:
# 0: homogeneous Kassel group (Treatment 1, 2, 3, 4)
# 1: heterogeneous group (Treatments 5, 6, 7, 8)
# 2: homogeneous Passau group (Treatment 1, 2, 3, 4)

# Group type represents whether participants should be placed in homogeneous (0)
PARTICIPANT_FIELDS = [
    'uni',
    'sequence',
    'group_type',
    'selected_round',
    'control_questions_payoff',
    'pgg_payoff',
    'punishment_pgg_payoff',
    'beliefs_correctly_guessed',
    'pgg_contribution',
    'pgg_payoff',
    'pgg_payoff_other_player',
    'pgg_contribution_received',
]

# Adding 2 additional session fields to access across the whole session and constant for all participants

# player_collections (array) is the matrix of the collection of players that will play with each other during
# the session. The matrix size is row_count = sequence_count * group_type_count;
# col_count = total_player_count / (sequence_count * group_type_count)

# groups_per_round (array) is the matrix of the player pairs (groups) for all the rounds, including round 0
# of the pgg game. The matrix size is: row_count = punishment_pgg_total_rounds  + 1; col_count = total_player_count/2

SESSION_FIELDS = ['player_collections', 'groups_per_round']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'de'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ROOMS = [
    {
        'name': 'DG_Game',
        'display_name' : 'DG_Game',
        'participant_label_file' : 'DG_Game.txt'
    }
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '1749229383192'

INSTALLED_APPS = ['otree']

