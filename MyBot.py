# keep these three import statements
import game_API
import fileinput
import json

# your import statements here
import random

first_line = True # DO NOT REMOVE

# global variables or other functions can go here
stances = ["Rock", "Paper", "Scissors"]

# find monster with defined input function
def monster_with_max_attribute(monsters, attribute_fn):
    max_monster = monsters[0]
    maxn = 0
    for monster in monsters:
        if attribute_fn(monster) > maxn:
            max_monster = monster
            maxn = attribute_fn(monster)

    return max_monster

def get_winning_stance(stance):
    if stance == "Rock":
        return "Paper"
    elif stance == "Paper":
        return "Scissors"
    elif stance == "Scissors":
        return "Rock"

def pick_dest_for_speed(game, me):
    destination_node = -1
    monsters = game.nearest_monsters(me.location, 1)


    for monster in monsters:
        if monster.death_effects.speed > 0:
            paths = game.shortest_paths(me.location, monster.location)
            destination_node = paths[random.randint(0, len(paths) - 1)][0]

    return destination_node

# returns amt health gained / lost from a fight
def health_diff_from_fight(game, me, destination_node):
    health_from_kill = game.get_monster(destination_node).death_effects.health

    num_turns = 7 - me.speed
    health_we_lose = monster.attack * num_turns

    return health_from_kill - health_we_lose

# checks if our destination will kill us
def dest_will_kill(game, me, destination_node):
    if (not game.has_monster(destination_node)):
        return False

    if me.health - health_diff_from_fight(game, me, destination_node) <= 0:
        return True
    else:
        return False

def random_move(game, me):
    # get all living monsters closest to me
    monsters = game.nearest_monsters(me.location, 1)

    # choose a monster to move to at random
    monster_to_move_to = monsters[random.randint(0, len(monsters)-1)]

    # get the set of shortest paths to that monster
    paths = game.shortest_paths(me.location, monster_to_move_to.location)
    destination_node = paths[random.randint(0, len(paths)-1)][0]

    return destination_node

# main player script logic
# DO NOT CHANGE BELOW ----------------------------
for line in fileinput.input():
    if first_line:
        game = game_API.Game(json.loads(line))
        first_line = False
        continue
    game.update(json.loads(line))
# DO NOT CHANGE ABOVE ---------------------------

    # code in this block will be executed each turn of the game

    me = game.get_self()

    s_weight = 0.5

    h_weight = 0.2
    r_weight = 0.2
    sc_weight = 0.2
    p_weight = 0.2

    if me.location == me.destination: # check if we have moved this turn
        destination_node = pick_dest_for_speed(game, me)

        if destination_node == -1 or dest_will_kill(game, me, destination_node):
            destination_node = random_move(game, me)

    else:
        destination_node = me.destination


    if game.has_monster(me.location):
        # if there's a monster at my location, choose the stance that damages that monster
        chosen_stance = get_winning_stance(game.get_monster(me.location).stance)
    else:
        # otherwise, pick a random stance
        chosen_stance = stances[random.randint(0, 2)]

    # submit your decision for the turn (This function should be called exactly once per turn)
    game.submit_decision(destination_node, chosen_stance)
