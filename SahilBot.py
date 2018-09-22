# keep these three import statements
import game_API
import fileinput
import json

# your import statements here
import random

first_line = True # DO NOT REMOVE

# global variables or other functions can go here
stances = ["Rock", "Paper", "Scissors"]
lastHealth = 100

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

    # choose your best stat stance (this will be overridden in most situations)
    maxStat = max(me.rock, me.paper, me.scissors)
    if maxStat == me.rock:
        chosen_stance = "Rock"
    elif maxStat == me.paper:
        chosen_stance = "Paper"
    else:
        chosen_stance = "Scissors"

    if game.has_monster(me.location):
        # if there's a monster at my location, choose the stance that damages that monster
        chosen_stance = get_winning_stance(game.get_monster(me.location).stance)
    if lastHealth - me.health > 1:
        # if you took damage last turn choose the stance that will beat the stance that beat you.
        chosen_stance = get_winning_stance(get_winning_stance(me.stance))
    if lastHealth == me.health:
        # if you won the battle, switch to what counters their counter of you
        chosen_stance = get_losing_stance(me.stance)

    lastHealth = me.health

    # submit your decision for the turn (This function should be called exactly once per turn)
    game.submit_decision(destination_node, chosen_stance)