from random import randint, seed
import numpy as np
import collections

################################
### NODE CLASS AND FUNCTIONS ###
################################

class Node:

  def __init__(self):
    self.neighbors = []

    # Set current values.
    self.color = None
    self.color_count = np.array([])
    self.colored_neighbors = 0

    # New values (updated at each iteration).
    self.new_color_count = np.array([])
    self.new_colored_neighbors = 0

  def init_color(self, color):
    self.color = color

    for neighbor in self.neighbors:
      neighbor.new_color_count[color] += 1
      neighbor.new_colored_neighbors += 1

  def remove_color(self):
    for neighbor in self.neighbors:
      neighbor.new_color_count[self.color] -= 1
      neighbor.new_colored_neighbors -= 1
    self.color = None

  def update_color(self, to_update):
    new_color = np.argmax(self.color_count)
    if self.color is not None and self.color_count[self.color] + 1.5 > self.color_count[new_color]:
      new_color = self.color

    if new_color != self.color and self.color_count[new_color] > self.colored_neighbors / 2.0:
      to_update.add(self)

      # Update neighbor count for neighboring nodes.
      for neighbor in self.neighbors:
        to_update.add(neighbor)
        neighbor.new_color_count[new_color] += 1
        if self.color is not None:
          neighbor.new_color_count[self.color] -= 1
        else:
          neighbor.new_colored_neighbors += 1

      # Update new values for this node (will become current at end of this iteration).
      self.color = new_color

      return True

    return False

  def complete_iteration(self):
    self.color_count = self.new_color_count.copy()
    self.colored_neighbors = self.new_colored_neighbors

  def reset(self, num_colors):
    self.color = None
    self.color_count = np.zeros(num_colors)
    self.new_color_count = np.zeros(num_colors)
    self.colored_neighbors = 0
    self.new_colored_neighbors = 0

  def check_node(self, where):
    sum = 0
    for neighbor in self.neighbors:
      if neighbor.color is not None:
        sum += 1
    if sum != self.new_colored_neighbors:
      print(f'other uh oh in {where}, sum={sum}, var={self.new_colored_neighbors}')

    if np.sum(self.new_color_count) != self.new_colored_neighbors:
      print(f'uh oh in {where}')


############################    
### SIMULATION FUNCTIONS ###
############################

def sim(nodes, seeds):
#   print(f'Seeds: {seeds}')
  # List of (index of color, labels of nodes to seed for this color)
  indexed_seeds = [(idx, seeds[key]) for (idx, key) in enumerate(seeds.keys())]
  num_colors = len(indexed_seeds)

  reset_nodes(nodes, num_colors)
  seed_nodes(nodes, indexed_seeds)
  max_rounds = randint(100, 200)
  iter = 0
  converged = False

  # print(f'Iteration {iter}:')
  # for node_key in nodes.keys():
  #   if nodes[node_key].color > 0:
  #     print(f'Node {node_key}, color: {nodes[node_key].color}')

  while iter < max_rounds and not converged:
    converged = iterate(nodes)
    iter += 1

    # print(f'Iteration {iter}:')
    # for node_key in nodes.keys():
    #   if nodes[node_key].color > 0:
    #     print(f'Node {node_key}, color: {nodes[node_key].color}')

  total_counts = np.zeros(num_colors)
  for node in nodes.values():
    if node.color is not None:
      total_counts[node.color] += 1

  return {color : total_counts[idx] for (idx, color) in enumerate(seeds.keys())}


def create_nodes(adj_list):
  nodes = {key : Node() for key in adj_list.keys()}  

  for key in nodes.keys():
    node = nodes[key]
    neighbors = adj_list[key]

    for neighbor_key in neighbors:
      neighbor = nodes[neighbor_key]
      node.neighbors.append(neighbor)

  return nodes

def reset_nodes(nodes, num_colors):
  for node in nodes.values():
    node.reset(num_colors)

def seed_nodes(nodes, indexed_seeds):
  conflicts = set()

  # Seed each node and keep track of conflicts.
  for (color, seed_nodes) in indexed_seeds:
    for node_label in seed_nodes:
      node = nodes[node_label]
      if node.color is not None:
        conflicts.add(node)
      else:
        # print(f'seeded node {node_label} with color {color}')
        node.init_color(color)

  # Resolve conflicts by setting node to have no color.
  for node in conflicts:
    node.remove_color()

  for node in nodes.values():
    node.complete_iteration()

def iterate(nodes):
  converged = True
  to_update = set()

  # First update colors according to voting scheme.
  for node in nodes.values():
    if node.update_color(to_update):
      converged = False
  
  # Set current values to new values when updates required.
  for node in to_update:
    node.complete_iteration()

  return converged



def sim_1v1(A, seed1, seed2):
    """
    Simulate a 2-color game on a given graph.

    Keyword arguments:
    A     -- modified (diagonals are 1.5) adjacency matrix form of the graph in column-major order.
    seed1 -- frozenset of indices representing color 1 seed nodes.
    seed2 -- frozenset of indices representing color 2 seed nodes.
    
    Returns:
    count1, count2 -- number of nodes for each color after convergence (or max iterations reached)
    """

    if seed1 == seed2:
        return 0.0, 0.0

    # Construct initial seeding for each color.
    n = A.shape[0]
    curr = np.zeros(n).reshape((-1,1))
    curr[list(seed1)] += 1
    curr[list(seed2)] -= 1

    # Simulate until convergence or max iterations reached
    max_iter = max_rounds = randint(100, 200)
    iter = 0
    prev = None

    while (prev != curr).any() and iter < max_iter:
        prev = curr
        curr = np.sign(A @ prev)
        iter += 1

    curr = np.array(curr).flatten()
    counts = collections.Counter(curr)
    return counts[1], counts[-1]

