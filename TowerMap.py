from platform import node
import copy
## BUILD CLASS

# node class
class MapNode:
  def __init__(self, key=0, value='0', tier = 100):
    self.key = key
    self.value = value
    self.tier = tier
    self.prev = {}
    self.next = {}

# hero class
class Hero:
  def __init__(self):
    self.health = 100
    self.attack = 10
    self.coin = 0

# monster class
class Monster:
  def __init__(self):
    self.m_health = 10
    self.m_attack = 4
    self.z_health = 10
    self.z_attack = 110  

node_set = {} # save visited node
hero = Hero()
monster = Monster()

## NODE OPERATIONS

# add edge between two nodes
def add_node(node_prev, node_next):
  node_prev.next[node_next.key] = node_next
  node_next.prev[node_prev.key] = node_prev

# delete one node from map
def delete_node(node_delete):
  for prev_key in node_delete.prev:
    node_prev = node_delete.prev[prev_key]
    node_prev.next.pop(node_delete.key)
    for next_key in node_delete.next:
      node_next = node_delete.next[next_key]
      if node_next.key == node_prev.key:
        continue
      node_prev.next[node_next.key] = node_next

# build the relational map  
que = [] 
root_node = MapNode(0, 'H', 0)
zeno_node = MapNode(0, 'Z', 0)
exit_node = MapNode(0, 'E', 0)
def buildMap(map, start_i, start_j):
  global root_node
  root_node = MapNode(start_i*100+start_j, 'H', 0)
  que.append(root_node)
  node_set[root_node.key] = root_node
  while ( len(que) != 0 ):
    size = len(que)
    for i in range(size):
      cur_node = que.pop(0)
      idx = cur_node.key // 100
      jdx = cur_node.key % 100
      tier = cur_node.tier
      visited = [[False]*len(map[0]) for i in range(len(map))]
      visited[idx][jdx] = True
      searchNeighbors(map, idx-1, jdx, tier, cur_node, visited)
      searchNeighbors(map, idx+1, jdx, tier, cur_node, visited)
      searchNeighbors(map, idx, jdx-1, tier, cur_node, visited)
      searchNeighbors(map, idx, jdx+1, tier, cur_node, visited)

# find neighbors of one node
def searchNeighbors(map, idx, jdx, tier, cur_node, visited):
  global zeno_node
  global exit_node
  if ( idx < 0 or jdx < 0 or idx > len(map)-1 or jdx > len(map[0])-1 ): return
  # is wall or visited cell
  if (map[idx][jdx] == '1' or visited[idx][jdx] == True): return
  visited[idx][jdx] = True
  # a node cell
  if (map[idx][jdx] != '0'):
    if ( (idx*100+jdx) in node_set ):
      past_node = node_set[idx*100+jdx]
      if past_node.tier == tier:
        add_node(cur_node, past_node)
    elif ( (idx*100+jdx) not in node_set ):
      neighbor_node = MapNode(idx*100+jdx, map[idx][jdx], tier+1)
      add_node(cur_node, neighbor_node)
      que.append(neighbor_node)
      node_set[idx*100+jdx] = neighbor_node
    if map[idx][jdx] == 'Z':
      zeno_node = MapNode(idx*100+jdx, map[idx][jdx], tier+1)
    if map[idx][jdx] == 'E':
      exit_node = MapNode(idx*100+jdx, map[idx][jdx], tier+1)
    return
  searchNeighbors(map, idx+1, jdx, tier, cur_node, visited)
  searchNeighbors(map, idx-1, jdx, tier, cur_node, visited)
  searchNeighbors(map, idx, jdx+1, tier, cur_node, visited)
  searchNeighbors(map, idx, jdx-1, tier, cur_node, visited)

map = [ ['1', '1', '1', '1', '1', '1', '1', '1', '1'],
 ['1', 'H', '0', 'M', '0', '1', 'c', 'c', '1'],
 ['1', '0', 'c', '1', 'c', '1', 'c', 'c', '1'],
 ['1', '1', 'c', '1', 'c', '0', 'M', '1', '1'],
 ['1', '0', '0', '1', '0', '1', '0', 'c', '1'],
 ['1', '0', '1', '1', 'M', '1', '1', '1', '1'],
 ['1', 'M', '0', '0', '0', 'M', '0', 'c', 'E'],
 ['1', 'S', '0', '0', '1', 'Z', '1', '0', '1'],
 ['1', '1', '1', '1', '1', '1', '1', '1', '1']]


## FIND PATH

# collect 'free' coin(don't have to beat a monster)
def collectCoin(cur_node):
  find = False
  neighbors_list = cur_node.next
  tmp = copy.deepcopy(neighbors_list)
  for key in tmp:
    if (key in node_set and neighbors_list[key].value == 'c'):
      find = True
      hero.health = hero.health + 4
      node_set.pop(key)
      delete_node(neighbors_list[key])
  return find

# Fight with Monster

def fight(monster_node):
  if monster_node.value == 'M':
    hero.health = hero.health - monster.m_attack
  else:
    hero.health = hero.health - monster.z_attack
  if hero.health <= 0:
    return False
  return True

## BUILD MAP

buildMap(map, 1, 1)
que.append(root_node)
collectCoin(root_node)
# collectCoin(root_node)
print(hero.health)

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
    

  