# keep these three import statements
import game_API
import fileinput
import json

# your import statements here
import random

first_line = True # DO NOT REMOVE

# global variables or other functions can go here
stances = ["Rock", "Paper", "Scissors"]

def get_winning_stance(stance):
    if stance == "Rock":
        return "Paper"
    elif stance == "Paper":
        return "Scissors"
    elif stance == "Scissors":
        return "Rock"

def get_losing_stance(stance):
    if stance == "Rock":
        return "Scissors"
    elif stance == "Paper":
        return "Rock"
    elif stance == "Scissors":
        return "Paper"

# main player script logic
# DO NOT CHANGE BELOW ----------------------------

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.insert(0,item)

    def pop(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

def most_common(lst):
    return max(set(lst), key=lst.count)

q = Queue()

is_flip = 0

last_me_stance = "None"
last_last_me_stance = "None"

def should_i_farm(me):
    if me.paper + me.scissors + me.rock >= 8:
        return False 
    if me.health < 40:
        return False
    return True

def eval_monster(game, monster):
    me = game.get_self()
    s_path = game.shortest_paths(me.location, monster.location)
    dis = len(s_path[0])
    time_require_to_move = (7 - me.speed) * dis
    stance_to_kill = get_winning_stance(monster.stance)
    time_require_to_kill = 0
    if stance_to_kill == "Rock":
        time_require_to_kill += me.rock
    elif stance_to_kill == "Scissors":
        time_require_to_kill += me.scissors
    elif stance_to_kill == "Paper":
        time_require_to_kill += me.paper
    time_require_all = time_require_to_move + time_require_to_kill
    # speed priority
    if monster.death_effects.speed > 0:
        time_require_all /= 2
    if monster.death_effects.health > 0 and me.health < 40:
        time_require_all = 0
    return time_require_all

for line in fileinput.input():
    if first_line:
        game = game_API.Game(json.loads(line))
        first_line = False
        continue
    game.update(json.loads(line))
# DO NOT CHANGE ABOVE ---------------------------

    # code in this block will be executed each turn of the game

    me = game.get_self()
    enemy = game.get_opponent();
    
    if me.location == me.destination: # check if we have moved this turn
        # get all living monsters closest to me
        monsters = game.nearest_monsters(me.location, 1)

        # monsters.sort(key=lambda x, y:cmp(eval_monster(game, x), eval_monster(game, y)))
        # choose a monster to move to at random
        to_move_to = monsters[0]

        if not should_i_farm(me):
            to_move_to = enemy

        # get the set of shortest paths to that monster
        paths = game.shortest_paths(me.location, to_move_to.location)
        destination_node = paths[random.randint(0, len(paths)-1)][0]
    else:
        destination_node = me.destination

    if game.has_monster(me.location):
        # if there's a monster at my location, choose the stance that damages that monster
        chosen_stance = get_winning_stance(game.get_monster(me.location).stance)
    else:
        # otherwise, pick a random stance
        chosen_stance = stances[random.randint(0, 2)]
    
    q.push(enemy.stance)

    if q.size() > 3:
        q.pop()

    if (enemy.location == me.location or enemy.location == me.destination) and enemy.stance in ["Rock", "Scissors", "Paper"]:
        chosen_stance = get_winning_stance(most_common(q.items))
        if enemy.stance == get_winning_stance(last_last_me_stance):
            is_flip += 1
        else:
            is_flip -= 1
        if is_flip >= 3:
            chosen_stance = get_winning_stance(get_winning_stance(last_me_stance))

    if chosen_stance not in ["Rock", "Scissors", "Paper"]:
        chosen_stance = "Rock"
    

    # submit your decision for the turn (This function should be called exactly once per turn)
    last_last_me_stance = last_me_stance
    last_me_stance = chosen_stance
    game.submit_decision(destination_node, chosen_stance)
    
