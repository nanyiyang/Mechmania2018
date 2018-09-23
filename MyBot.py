# keep these three import statements
import game_API
import fileinput
import json

# your import statements here
import random
import math

first_line = True # DO NOT REMOVE

# global variables or other functions can go here
stances = ["Rock", "Paper", "Scissors"]

# best path
best_path = [0, 10, 16, 10, 0, 6, 7, 8, 14, 19, 23, 19, 22, 12, 11, 10, 0]

def get_winning_stance(stance):
    if stance == "Rock":
        return "Paper"
    elif stance == "Paper":
        return "Scissors"
    elif stance == "Scissors":
        return "Rock"

# best path na (0, 1, 0, 10, 16, 12, 22, 21 -> random)
def hard_coded_path(game, me):

    if len(best_path) >= 1 and we_should_change_dest(game, me):
       best_path.pop(0)

    if len(best_path) == 0:
        return 0

    destination_node = best_path[0]

    return destination_node

def we_should_change_dest(game, me):
    will_kill_monster_in_time = False

    if time_to_kill_monster(game, me, me.location) >= 0:
        will_kill_monster_in_time = ((time_to_kill_monster(game, me, me.location)) < (me.movement_counter - me.speed))

    return me.location == best_path[0] and (not game.has_monster(me.location)
                                or (game.has_monster(me.location) and
                                 not game.get_monster(me.location).dead
                                 and will_kill_monster_in_time))

# returns number of turns it will take to kill the monster at that location
def time_to_kill_monster(game, me, location):
    if not game.has_monster(location):
        return -1

    monster = game.get_monster(location)
    wstance = get_winning_stance(monster.stance)

    strength = strength_of_stance(me, wstance)
    if strength == -1:
        return -1
    else:
        return math.ceil(monster.health / strength)

# returns player's strength in said stance
# return -1
def strength_of_stance(me, stance):
    if stance == "Rock":
        return me.rock
    elif stance == "Scissors":
        return me.scissors
    elif stance == "Paper":
        return me.paper
    else:
        return -1

def pick_for_HARD_SPEED(game, me):
    destination_node = -1

    monster = monster_alive_with_max_attribute(game.get_all_monsters(),
                                lambda x: x.death_effects.speed)

    paths = game.shortest_paths(me.location, monster.location)
    destination_node = paths[random.randint(0, len(paths) - 1)][0]

    return destination_node

def monster_alive_with_max_attribute(monsters, attribute_fn):
    max_monster = monsters[0]
    maxn = 0
    for monster in monsters:
        if attribute_fn(monster) > maxn and not monster.dead:
            max_monster = monster
            maxn = attribute_fn(monster)

    return max_monster

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
    """
    if me.location == me.destination: # check if we have moved this turn

        destination_node = pick_for_HARD_SPEED(game, me)

        #destination_node = random_move(game, me)
    else:
        destination_node = me.destination
    """
    destination_node = hard_coded_path(game, me)

    if game.has_monster(me.location):
        # if there's a monster at my location, choose the stance that damages that monster
        chosen_stance = get_winning_stance(game.get_monster(me.location).stance)
    else:
        # otherwise, pick a random stance
        if game.has_monster(destination_node):

        chosen_stance = stances[random.randint(0, 2)]

    # submit your decision for the turn (This function should be called exactly once per turn)
    game.submit_decision(destination_node, chosen_stance)
