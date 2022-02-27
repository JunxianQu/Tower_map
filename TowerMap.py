import copy
from collections import defaultdict
import heapq as heap
from typing import Tuple, Type

NodeMap = dict[int, 'MapNode']


# node class
class MapNode:
    def __init__(self, key=0, value='0', tier=100):
        self.key = key
        self.value = value  # type
        self.tier = tier  # number of steps to reach (redundant)
        self.next: NodeMap = {}

    def __repr__(self):
        return f"key: {self.key}, value: {self.value}, tier: {self.tier}"

    def __lt__(self, other):
        return self.key < other.key


class Hero:
    # hero class
    def __init__(self):
        self.health = 100
        self.attack = 10
        self.coin = 0


class Monster:
    # monster class
    def __init__(self):
        self.m_health = 10
        self.m_attack = 4
        self.z_health = 10
        self.z_attack = 110


def add_node(node_a, node_b):
    # add edge between two nodes
    node_a.next[node_b.key] = node_b
    node_b.next[node_a.key] = node_a


# delete one node from map
def delete_node(node_delete: MapNode):
    for node_a in node_delete.next.values():
        node_a.next.pop(node_delete.key)
        for node_b in node_delete.next.values():
            if node_a.key == node_b.key:
                continue
            node_a.next[node_b.key] = node_b
            node_b.next[node_a.key] = node_a


def hash_fn(x: int, y: int) -> int:
    return x * 100 + y


def inv_hash(z: int):
    return z // 100, z % 100


class TowerMap:
    def __init__(self,
                 graph,
                 start_i: int,
                 start_j: int) -> None:
        self.costs = None
        self.path = None
        self.start_j = start_j
        self.start_i = start_i
        self.graph = graph
        self.que = []
        self.node_set = {}
        self.root_node = MapNode(0, 'H', 0)
        self.zeno_node = MapNode(0, 'Z', 0)
        self.exit_node = MapNode(0, 'E', 0)
        self.build_map()
        self.hero = Hero()
        self.monster = Monster()
        self.pl_hp = 4

    def build_map(self) -> None:
        self.root_node = MapNode(hash_fn(self.start_i, self.start_j), 'H', 0)
        self.que.append(self.root_node)
        self.node_set[self.root_node.key] = self.root_node
        while len(self.que) != 0:
            size = len(self.que)
            for i in range(size):
                cur_node = self.que.pop(0)
                idx, jdx = inv_hash(cur_node.key)
                tier = cur_node.tier
                visited = [[False] * len(self.graph[0]) for i in range(len(self.graph))]
                visited[idx][jdx] = True
                self.search_neighbors(idx - 1, jdx, tier, cur_node, visited)
                self.search_neighbors(idx + 1, jdx, tier, cur_node, visited)
                self.search_neighbors(idx, jdx - 1, tier, cur_node, visited)
                self.search_neighbors(idx, jdx + 1, tier, cur_node, visited)

    def search_neighbors(self, idx: int, jdx: int, tier: int, cur_node, visited):
        # find neighbors of one node DFS
        if idx < 0 or jdx < 0 or idx > len(self.graph) - 1 or jdx > len(self.graph[0]) - 1:
            return
        # is wall or visited cell
        if self.graph[idx][jdx] == '1' or visited[idx][jdx] is True:
            return
        visited[idx][jdx] = True
        # a node cell
        if self.graph[idx][jdx] != '0':
            if (hash_fn(idx, jdx)) in self.node_set:
                past_node = self.node_set[idx * 100 + jdx]
                if past_node.tier == tier:
                    add_node(cur_node, past_node)
            elif (hash_fn(idx, jdx)) not in self.node_set:
                neighbor_node = MapNode(idx * 100 + jdx, self.graph[idx][jdx], tier + 1)
                add_node(cur_node, neighbor_node)
                self.que.append(neighbor_node)
                self.node_set[hash_fn(idx, jdx)] = neighbor_node
            if self.graph[idx][jdx] == 'Z':
                self.zeno_node = MapNode(hash_fn(idx, jdx), self.graph[idx][jdx], tier + 1)
            if self.graph[idx][jdx] == 'E':
                self.exit_node = MapNode(hash_fn(idx, jdx), self.graph[idx][jdx], tier + 1)
            return
        self.search_neighbors(idx + 1, jdx, tier, cur_node, visited)
        self.search_neighbors(idx - 1, jdx, tier, cur_node, visited)
        self.search_neighbors(idx, jdx + 1, tier, cur_node, visited)
        self.search_neighbors(idx, jdx - 1, tier, cur_node, visited)

    def delete_node(self, key):
        delete_node(self.node_set[key])
        self.node_set.pop(key)

    def collect_coin_1round(self) -> bool:
        # collect 'free' coin(don't have to beat a monster) 1 round
        cur_node = self.root_node
        find = False
        neighbors_list = cur_node.next
        tmp = copy.deepcopy(neighbors_list)
        for key in tmp:
            if key in self.node_set and neighbors_list[key].value == 'c':
                find = True
                self.hero.health = self.hero.health + self.pl_hp
                print(f"get coin at {key}")
                self.delete_node(key)
        return find

    def collect_coin(self) -> bool:
        res = self.collect_coin_1round()
        flag = res
        while res:
            res = self.collect_coin_1round()
        return flag

    def collect_powerful(self):
        cur_node = self.root_node
        find = False
        neighbors_list = cur_node.next
        tmp = copy.deepcopy(neighbors_list)
        for key in tmp:
            if neighbors_list[key].value == 'M':
                vis = set()
                reward = self.check_reward(key, vis)
                alive = self.hero.health - self.monster.m_attack > 0
                if reward >= self.monster.m_attack and alive:
                    self.fight(neighbors_list[key])
                    self.delete_node(key)
                    self.collect_coin()
                    find = True
        return find

    def check_reward(self, pos, vis: set) -> int:
        reward = 0
        for key in self.node_set[pos].next:
            if self.node_set[key].value == 'c' and key not in vis:
                vis.add(key)
                reward += self.pl_hp
                reward += self.check_reward(key, vis)
        return reward

    def dijkstra(self):
        visited = set()
        parents_map = {}
        pq = []
        node_costs = defaultdict(lambda: float('inf'))
        node_costs[self.root_node.key] = 0
        heap.heappush(pq, (0, self.root_node))

        while pq:
            # go greedily by always extending the shorter cost nodes first
            _, cur_node = heap.heappop(pq)
            visited.add(cur_node.key)

            for adjNode in cur_node.next.values():
                if adjNode in visited:
                    continue

                if adjNode.value == 'M':
                    cost = self.monster.m_attack
                elif adjNode.value == 'Z':
                    cost = self.monster.z_attack
                else:
                    cost = 0

                newCost = node_costs[cur_node.key] + cost
                if node_costs[adjNode.key] > newCost:
                    parents_map[adjNode.key] = cur_node
                    node_costs[adjNode.key] = newCost
                    heap.heappush(pq, (newCost, adjNode))
        self.path = parents_map
        self.costs = node_costs
        return parents_map, node_costs

    def fight(self, monster_node) -> bool:
        # Fight with Monster
        print(f"fight with {monster_node.key}, {monster_node.value}, hero health:{self.hero.health}")
        if monster_node.value == 'M':
            self.hero.health = self.hero.health - self.monster.m_attack
        else:
            self.hero.health = self.hero.health - self.monster.z_attack
        if self.hero.health <= 0:
            return False

        return True


def simulation(tm: TowerMap) -> bool:
    path_list = []
    cur = tm.zeno_node.key
    while cur != tm.root_node.key:
        if tm.node_set[cur].value == 'M' or tm.node_set[cur].value == 'Z':
            path_list.append(cur)
        cur = tm.path[cur].key
    path_list.reverse()
    test = copy.deepcopy(tm)
    res = test.collect_powerful()
    while res:
        res = test.collect_powerful()
    for key in path_list:
        res = True
        test.collect_powerful()

        if key in test.node_set:
            res = test.fight(test.node_set[key])
            # print(test.node_set[key], res, test.hero.health)
            if not res:
                return res
            test.delete_node(key)

    return True

# print code

# que.append(root_node)

# while(len(que) != 0):
# size = len(que)
# for s in range(size):
#   cur_node = que.pop(0)
#   # print( 'first: '+(str)(len(que)))
#   # print(cur_node.key)
#   if( cur_node.key in node_set):
#     node_set.pop(cur_node.key)
#   print('i:'+(str)(cur_node.key//100)+', j:' + (str)(cur_node.key%100) + ', value: ' + cur_node.value)
#   for neighbor in cur_node.next:
#     if( neighbor in node_set):
#       que.append(cur_node.next[neighbor])