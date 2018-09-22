import json
import sys

class DeathEffects:
    def __init__(self, jsn):
        self.rock = jsn["Rock"]
        self.paper = jsn["Paper"]
        self.scissors = jsn["Scissors"]
        self.health = jsn["Health"]
        self.speed = jsn["Speed"]

class Player:
    def __init__(self, player_num):
        self.player_num = player_num
        self.name = "Player" + str(player_num)
        self.stance = "Invalid Stance"
        self.health = 20
        self.speed = 0
        self.movement_counter = 7
        self.location = 0
        self.destination = 0
        self.dead = False
        self.rock = 1
        self.paper = 1
        self.scissors = 1

    def update(self, jsn):
        self.name = jsn["Name"]
        self.stance = jsn["Stance"]
        self.health = jsn["Health"]
        self.speed = jsn["Speed"]
        self.movement_counter = jsn["Movement Counter"]
        self.location = jsn["Location"]
        self.destination = jsn["Destination"]
        self.dead = jsn["Dead"]
        self.rock = jsn["Rock"]
        self.paper = jsn["Paper"]
        self.scissors = jsn["Scissors"]

class Monster:
    def __init__(self, jsn):
        if jsn is None:
            self.name = "No Monster"
            self.stance = "Invalid Stance"
            self.health = 0
            self.respawn_rate = 0
            self.respawn_counter = 0
            self.location = 0
            self.dead = False
            self.death_effects = 0
            self.attack = 0
            self.base_health = 0
        else:
            self.name = jsn["Name"]
            self.stance = jsn["Stance"]
            self.health = jsn["Health"]
            self.respawn_rate = 7 - jsn["Speed"]
            self.respawn_counter = 0
            self.location = jsn["Location"]
            self.dead = False
            self.death_effects = DeathEffects(jsn["Death Effects"])
            self.attack = jsn["Attack"]
            self.base_health = self.health

    def update(self, jsn):
        self.name = jsn["Name"]
        self.stance = jsn["Stance"]
        self.health = jsn["Health"]
        self.respawn_rate = 7 - jsn["Speed"]
        self.respawn_counter = jsn["Movement Counter"] - jsn["Speed"]
        self.location = jsn["Location"]
        self.destination = jsn["Destination"]
        self.dead = jsn["Dead"]
        self.attack = jsn["Attack"]
        self.base_health = jsn["Base Health"]

class Node:
    def __init__(self, jsn):
        self.adjacents = []

    def add_adjacent(self, n):
        self.adjacents.append(n)

class Game:
    def __init__(self, jsn):
        self.turn_number = 0
        self.player_num = jsn["player_id"]
        map_json = json.loads(jsn["map"])

        self.nodes = [Node(j) for j in map_json["Nodes"]]

        for edge_json in map_json["Edges"]:
            adj = edge_json["Adjacents"]
            self.nodes[adj[0]].add_adjacent(adj[1])
            self.nodes[adj[1]].add_adjacent(adj[0])

        self.monsters = [Monster(j) for j in map_json["Monsters"]]

        self.player1 = Player(1)
        self.player2 = Player(2)

    def update(self, jsn):
        self.turn_number = jsn["turn_number"]

        for unit_json in jsn["game_data"]:
            if unit_json["Type"] == "Player":
                if unit_json["Name"] == "Player1":
                    self.player1.update(unit_json)
                else:
                    self.player2.update(unit_json)
            else:
                for monster in self.monsters:
                    if monster.location == unit_json["Location"]:
                        monster.update(unit_json)
                        break

    def log(self, str):
        if (self.player_num == 1):
            sys.stderr.write("Player1: " + str + "\n")
        else:
            sys.stderr.write("Player2: " + str + "\n")
        sys.stderr.flush()

    def get_duel_turn_num(self):
        return 300

    def get_turn_num(self):
        return self.turn_number

    def get_adjacent_nodes(self, node):
        return self.nodes[node].adjacents

    def get_all_monsters(self):
        return self.monsters

    def get_self(self):
        if self.player_num == 1:
            return self.player1
        else:
            return self.player2

    def get_opponent(self):
        if self.player_num == 1:
            return self.player2
        else:
            return self.player1

    def submit_decision(self, destination, stance):
        j = dict()

        j["Dest"] = destination
        j["Stance"] =stance

        print(json.dumps(j))
        sys.stdout.flush()

    def shortest_paths(self, start, end):
        distance = [-1 for n in self.nodes]
        parent_dict = {n : [] for n in range(len(self.nodes))}
        explored = [False for n in self.nodes]

        to_visit = [start]
        distance[start] = 0

        while not explored[end]:
            n = to_visit.pop(0)

            for adj in self.nodes[n].adjacents:
                if not explored[adj]:
                    if distance[adj] == -1:
                        distance[adj] = distance[n] + 1
                        parent_dict[adj].append(n)
                        to_visit.append(adj)
                    elif distance[adj] == distance[n] + 1:
                        parent_dict[adj].append(n)
            explored[n] = True

        paths = [[end]]
        reached_start = (end == start)

        while not reached_start:
            new_paths = []
            for path in paths:
                for parent in parent_dict[path[0]]:
                    if parent == start:
                        reached_start = True
                    else:
                        new_path = [n for n in path]
                        new_path.insert(0, parent)
                        new_paths.insert(0, new_path)
            if not reached_start:
                paths = new_paths

        return paths

    def has_monster(self, node):
        for monster in self.monsters:
            if monster.location == node:
                return True
        return False

    def get_monster(self, node):
        for monster in self.monsters:
            if monster.location == node:
                return monster
        return Monster(None)

    def get_monster_valid_function(self, search_mode):
        if search_mode == 0:
            return lambda m : True
        elif search_mode == 1:
            return lambda m : (m.dead == False)
        elif search_mode == 2:
            return lambda m : (m.dead == True)

    def get_monster_valid_function_name(self, search_mode, name):
        if search_mode == 0:
            return lambda m : (m.name == name)
        elif search_mode == 1:
            return lambda m : (m.dead == False and m.name == name)
        elif search_mode == 2:
            return lambda m : (m.dead == True and m.name == name)

    def nearest_monsters(self, node, search_mode):
        return self.nearest_monsters_helper(node, self.get_monster_valid_function(search_mode))

    def nearest_monsters_with_name(self, node, name, search_mode):
        return self.nearest_monsters_helper(node, self.get_monster_valid_function_name(search_mode, name))

    def nearest_monsters_helper(self, node, monster_valid):
        valid_monsters = [None for n in self.nodes]
        found_valid = False
        for mon in self.monsters:
            if (monster_valid(mon)):
                valid_monsters[mon.location] = mon
                found_valid = True

        if not found_valid:
            return []

        explored = []
        to_explore = [node]
        distances = [-1 for n in self.nodes]
        distances[node] = 0

        ret = []

        min_dist = -1
        done = False
        while not done:
            n = to_explore.pop(0)

            for adj in self.nodes[n].adjacents:
                if (distances[adj] == -1):
                    distances[adj] = distances[n] + 1

                if adj not in explored and adj not in to_explore:
                    to_explore.append(adj)

            if (min_dist != -1 and distances[n] > min_dist):
                return ret

            if valid_monsters[n] is not None:
                ret.append(valid_monsters[n])

                if min_dist == -1:
                    min_dist = distances[n]

            if len(to_explore) == 0:
                return ret
