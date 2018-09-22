# keep these three import statements
import game_API
import fileinput
import json

# your import statements here
import random
import math

first_line = True  # DO NOT REMOVE

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
    a = 1  # amplitude
    k = 0.5  # steepness
    h = 0  # horizontal offset

    return a/(1+math.e**(k*(x-h)))


def bell_curve(x):
    h = 4  # horizontal offset
    # returns value between 0 and 1
    return (math.e**(h-x))**(x-h)


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
            value = value + 0.5*(7-me.speed)*monster.death_effects.speed
            # Weight for heath
            value = value + 6*(health_diff_from_fight(game, me, monster.location))*monster.death_effects.health

            statTotal = me.rock + me.paper + me.scissors
            # Weight for rock stat
            value = value + (game.get_opponent().scissors * statTotal / me.rock)*monster.death_effects.rock
            # Weight for paper stat
            value = value + (game.get_opponent().rock * statTotal / me.paper) * monster.death_effects.paper
            # Weight for scissors stat
            value = value + (game.get_opponent().paper * statTotal / me.scissors) * monster.death_effects.scissors

            # divide the value by the distance to the monster (bell_curve makes values in the middle the best)
            value = value*opposite_logistic(len(game.shortest_paths(me.location, monster.location)[0]))

            # checks if monster will kill you
            if dest_will_kill(game, me, monster.location):
                value = -1000
        monster_values.append(value)

    target_monster = game.get_all_monsters()[target_monster_index]
    if target_monster_index is -1 or me.location == target_monster.location or target_monster.dead:
        # target the monster with the highest value
        target_monster_index = monster_values.index(max(monster_values))
        target_monster = game.get_all_monsters()[target_monster_index]

    if len(path) != 0 and me.location == me.destination and me.location == path[0]:
        if not game.has_monster(me.location) or game.has_monster(me.location) and game.get_monster(me.location).dead:
            # remove path[0] and move on to the next node
            path.pop(0)

    if (not game.has_monster(me.location) or (game.has_monster(me.location) and game.get_monster(me.location).dead)) and len(path) == 0:
        i = random.randint(0, len(game.shortest_paths(me.location, target_monster.location)) - 1)
        path = game.shortest_paths(me.location, target_monster.location)[i]
    elif len(path) == 0:
        path.append(me.location)

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

    game.log("Turn: {0}, Final_Destination: {1}, Current Location: {2}".format(game.turn_number, path[-1], me.location))

    # submit your decision for the turn (This function should be called exactly once per turn)
    game.submit_decision(destination_node, chosen_stance)
