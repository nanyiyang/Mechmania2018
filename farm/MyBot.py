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
lastHealth = 100
target_monster_index = -1
path = []


def get_winning_stance(stance):
    if stance == "Rock":
        return "Paper"
    elif stance == "Paper":
        return "Scissors"
    elif stance == "Scissors":
        return "Rock"

# Note: get_winning_stance(get_winning_stance(stance)) == get_losing_stance(stance)


def get_losing_stance(stance):
    if stance == "Rock":
        return "Scissors"
    elif stance == "Paper":
        return "Rock"
    elif stance == "Scissors":
        return "Paper"


def opposite_logistic(x):
    a = 3
    k = 0.5
    h = 100

    return a/(1+math.e**(k*(x-h)))


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
        # get all living monsters closest to me
        monsters = game.nearest_monsters(me.location, 1)
        # choose a monster to move to at random
        monster_to_move_to = monsters[0]
        # get the set of shortest paths to that monster
        paths = game.shortest_paths(me.location, monster_to_move_to.location)
        destination_node = paths[random.randint(0, len(paths)-1)][0]
    else:
        destination_node = me.destination
    """

    # choose destination by rating all monsters
    monster_values = []
    for monster in game.get_all_monsters():
        value = 0
        if not monster.dead:
            # Weight for speed
            value = value + (7-me.speed + opposite_logistic(game.turn_number))*monster.death_effects.speed
            # Weight for heath (100 = base health)
            value = value + (100 - me.health)*monster.death_effects.health

            statTotal = me.rock + me.paper + me.scissors
            # Weight for rock stat
            value = value + (10* statTotal / me.rock)*monster.death_effects.rock
            # Weight for paper stat
            value = value + (10 * statTotal / me.paper) * monster.death_effects.paper
            # Weight for scissors stat
            value = value + (10 * statTotal / me.scissors) * monster.death_effects.scissors

            # deduct from value based on attack
            value = value - monster.attack
            # divide the value by the distance to the monster
            value = value/len(game.shortest_paths(me.location, monster.location)[0])

            # checks if monster will kill you
            if monster.attack > me.health:
                value = 0
        monster_values.append(value)

    game.log("turn: {0}, values: {1}, best_monster: {2}".format(game.turn_number, monster_values, target_monster_index))

    target_monster = game.get_all_monsters()[target_monster_index]
    if target_monster_index is -1 or me.location == target_monster.location or target_monster.dead:
        # target the monster with the highest value
        target_monster_index = monster_values.index(max(monster_values))
        target_monster = game.get_all_monsters()[target_monster_index]

    if game.shortest_paths(me.location, target_monster.location)[0] != path or len(path) == 0:
        path = game.shortest_paths(me.location, target_monster.location)[0]

    if me.location == me.destination and me.location == path[0] and not game.has_monster(me.location):
        # remove path[0] and move on to the next node
        path.pop(0)

    game.log("turn: {0}, current_path: {1}, possible_path: {2}".format(game.turn_number, path, game.shortest_paths(me.location, target_monster.location)[0]))
    destination_node = path[0]

    # choose your best stat stance (this will be overridden in most situations)
    maxStat = max(me.rock, me.paper, me.scissors)
    if maxStat == me.rock:
        chosen_stance = "Rock"
    elif maxStat == me.paper:
        chosen_stance = "Paper"
    else:
        chosen_stance = "Scissors"

    if game.get_opponent().location == me.location:
        if lastHealth - me.health > 1:
            # if you took damage last turn choose the stance that will beat the stance that beat you.
            # if you won the battle, switch to what counters their counter of you
            chosen_stance = get_losing_stance(me.stance)
    elif game.has_monster(me.location):
        # if there's a monster at my location, choose the stance that damages that monster
        chosen_stance = get_winning_stance(game.get_monster(me.location).stance)

    lastHealth = me.health

    # submit your decision for the turn (This function should be called exactly once per turn)
    game.submit_decision(destination_node, chosen_stance)