from random import randrange
from time import sleep
from math import floor
from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gender = models.StringField(
        label='Welches Geschlecht haben Sie?',
        choices=['Weiblich', 'Männlich', 'Divers', 'Keine Antwort'],
        widget=widgets.RadioSelect
    )

    age = models.IntegerField(
        label='In welchem Jahr wurden Sie geboren?'
    )

    degree = models.StringField(
        label='Was ist Ihr höchster Abschluss?',
        choices=['Abitur', 'Bachelor', 'Master', 'Anderer Abschluss'],
        widget=widgets.RadioSelect
    )

    uni = models.IntegerField(
        choices=[[0, 'Universität Kassel'], [1, 'Universität Passau']],
    )

    uni_declared = models.IntegerField(
        label='An welcher Universität studieren Sie?',
        choices=[[0, 'Universität Kassel'], [1, 'Universität Passau']],
        widget=widgets.RadioSelect,
    )
    sequence = models.IntegerField
    group_type = models.IntegerField

    prime = models.StringField(label='')


# FUNCTIONS
def prepare_group_types(group):
    players = group.get_players()

    # assign uni depending on survey answer
    for player in players:
        player.uni = 0 if player.participant.label.split('_')[0] == 'K' else 1
        player.participant.uni = 0 if player.participant.label.split('_')[0] == 'K' else 1
        # player.participant.uni = player.id_in_group % 2  # temp solution to split in exact 50/50 - Disable for prod
        # player.uni = player.id_in_group % 2 # temp solution to split in exact 50/5 - Disable for prod

    # The next section equally divide participants in the three group types and assigns their corresponding value
    # in their participant field

    num_participants = group.session.num_participants
    players = player.subsession.get_players()

    # groups should be such that exactly 50% are homogeneous and 50% heterogeneous
    num_participants_in_homogeneous_groups = num_participants / 2
    num_participants_in_heterogeneous_groups = num_participants / 4

    players_in_group_type_0 = []
    players_in_group_type_2 = []

    # pick players at random in the list as long as it is from uni 0 and until we reach the desired total
    while len(players_in_group_type_0) < num_participants_in_heterogeneous_groups:
        random_index = randrange(len(players))
        if players[random_index].uni == 0:
            players_in_group_type_0.append(players.pop(random_index))

    # same for the other uni
    while len(players_in_group_type_2) < num_participants_in_heterogeneous_groups:
        random_index = randrange(len(players))
        if players[random_index].uni == 1:
            players_in_group_type_2.append(players.pop(random_index))

    # everyone left should constitute a group of the expected size
    if len(players) != num_participants_in_homogeneous_groups:
        raise Exception("Could not split players in equal group types ")

    # Save outcome at participant level
    for player in players_in_group_type_0:
        player.participant.group_type = 0
        player.group_type = 0

    for player in players_in_group_type_2:
        player.participant.group_type = 2
        player.group_type = 0

    for player in players:
        player.participant.group_type = 1
        player.group_type = 1

    return [players_in_group_type_0[:], players[:], players_in_group_type_2[:]]


def collections_from_groups(group, group_types):
    # Next we have to assign participants randomly to each treatment within their group
    # This creates 12 collections that we then store in the player_collections matrix
    num_participants = group.session.num_participants
    player_collections = [[] for i in range(12)]
    collection_index = 0
    for sequence_index in range(4):
        for group_index in range(3):
            # homogeneous groups have fewer people but also fewer constraints
            if group_index % 2 == 0:
                participants_per_collection = num_participants / (2 * 2 * 4)
                # until we fill the collection, we pick new random players within the corresponding group
                while len(player_collections[collection_index]) < participants_per_collection and len(
                        group_types[group_index]) > 0:
                    picked_player = group_types[group_index].pop(randrange(len(group_types[group_index])))
                    picked_player.participant.sequence = sequence_index % 4
                    picked_player.sequence = sequence_index % 4
                    player_collections[collection_index].append(picked_player)
            else:
                # heterogeneous collections have double the amount of participants but also need to balance the
                # groups between unis
                participants_per_collection = num_participants / (2 * 4)
                parity = [0, 0]
                # until we fill the collection, we pick new random players within the corresponding group
                while len(player_collections[collection_index]) < participants_per_collection and len(
                        group_types[group_index]) > 0:
                    picked_player_index = randrange(len(group_types[group_index]))
                    # check if we already have not yet reach half the group with one uni
                    if parity[group_types[group_index][picked_player_index].uni] < (participants_per_collection / 2):
                        picked_player = group_types[group_index].pop(picked_player_index)
                        parity[picked_player.uni] += 1
                        picked_player.participant.sequence = sequence_index % 4
                        picked_player.sequence = sequence_index % 4
                        player_collections[collection_index].append(picked_player)
            collection_index += 1
    return player_collections


def set_groups_per_round(group, player_collections):

    # Now we need to create the matrix of all rounds (groups_per_round), for each round, for each collection,
    # we pick a random player and match it with another random player within the same collection,
    # as long as this couple was not already paired in a previous round
    #
    # The total number of rounds = 1 + session.config['punishment_pgg_total_rounds'] and
    # !!!! punishment_pgg_total_rounds MUST match the NUM_ROUNDS in the punishment_pgg game constants !!!!

    total_num_rounds = 1 + group.session.config['punishment_pgg_total_rounds']
    groups_per_round = None
    all_groups_found = False
    attempt_number = 0
    while not all_groups_found:
        # for each round
        stop = False
        groups_per_round = []
        attempt_number += 1
        for r in range(total_num_rounds):
            # fill up the array of pairings for the given round
            round_pairings = []
            # for each collection, stay within a collection
            for collection in player_collections:
                # extract a copy of the collection to keep track of players to place within a collection
                players_to_match = collection[:]
                # until we placed all players from that collection, do
                while len(players_to_match) > 0 and not stop:
                    # pick a random player and extract it from the list
                    first_player = players_to_match.pop(randrange(len(players_to_match)))
                    # print(f'Trying to match {first_player} in round {r} within collection')
                    # print(collection)
                    placed = False
                    # keep track of attempts to find a pairing with a matrix of all other players
                    attempts = players_to_match[:]

                    # until we succeeded do
                    while not placed and not stop:
                        # if there are no more possible options, start over again
                        if len(attempts) == 0:
                            stop = True
                        else:
                            # pick a second player from the potential ones
                            second_player = attempts.pop(randrange(len(attempts)))
                            # if they are in the same uni and in a homogeneous group, then skip
                            if first_player.participant.group_type != 1 or first_player.uni != second_player.uni:
                                # print(f'With {second_player}')
                                placeable = True
                                # check in all previously defined rounds if this pairing already existed
                                for existing_rounds in groups_per_round:
                                    for pair in existing_rounds:
                                        if first_player in pair and second_player in pair:
                                            # if it existed, do not place here
                                            placeable = False
                                            # print(f'Did not work, trying again')
                                # if there was no problem, then add the pair to the list
                                # and remove second player from the players_to_match as well
                                if placeable:
                                    new_pair = [first_player,
                                                players_to_match.pop(players_to_match.index(second_player))]
                                    # print(f'Worked, this is the new pair {new_pair}')
                                    round_pairings.append(new_pair)
                                    placed = True
            # once done with each collection, add the corresponding round_pairings to the matrix
            groups_per_round.append(round_pairings)
        all_groups_found = [] not in groups_per_round
    id_matrix = player_matrix_into_id_matrix(groups_per_round)
    group.session.groups_per_round = id_matrix
    print(id_matrix)
    return groups_per_round


# Convert the matrix of player per round into a matrix of id
def player_matrix_into_id_matrix(groups_per_round):
    rounds_matrix = []
    for r in groups_per_round:
        round_matrix = []
        for pair in r:
            id_pair = []
            for player in pair:
                id_pair.append(player.participant.id_in_session)
            round_matrix.append(id_pair)
        rounds_matrix.append(round_matrix)
    return rounds_matrix


# Convert the matrix of player per round into a matrix of id
def groups_matrix_into_id_matrix(group_types):
    id_matrix = []
    for player_group in group_types:
        id_group = []
        for player in player_group:
            id_group.append(player.participant.id_in_session)
        id_matrix.append(id_group)
    return id_matrix


def prepare_collections_and_groups(group):
    # split players into 3 groups
    group_types = prepare_group_types(group)
    # assign players into 12 different collections based on groups - not needed when single treatment per session
    # player_collections = collections_from_groups(group, group_types)
    # assign pairs for each round based on collections
    set_groups_per_round(group, group_types)


def push_uni_to_session(group):
    players = group.get_players()
    for player in players:
        player.participant.uni = player.field_maybe_none('uni')


# PAGES
class Demographics(Page):
    form_model = 'player'
    form_fields = ['gender', 'age', 'degree', 'uni_declared']


class Instructions(Page):
    pass


class Prime(Page):
    form_model = 'player'
    form_fields = ['prime']


class PrepareCollectionsAndGroups(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        if group.session.config['test_mode']:
            push_uni_to_session(group)
        else:
            prepare_collections_and_groups(group)

    body_text = "Bitte warten. Das Spiel wird in kürze weitergehen."


page_sequence = [Instructions, Demographics, PrepareCollectionsAndGroups]
