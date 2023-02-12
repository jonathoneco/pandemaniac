from random import randint, seed
import numpy as np

################################
### NODE CLASS AND FUNCTIONS ###
################################

class Node:

  def __init__(self):
    self.neighbors = []

    # Set current values.
    self.color = 0
    self.neighbor_count = np.array([])
    self.colored_neighbors = 0

    # New values (updated at each iteration).
    self.new_color = self.color
    self.new_neighbor_count = self.neighbor_count.copy()
    self.new_colored_neighbors = self.colored_neighbors

  def init_color(self, color):
    self.new_color = color

    for neighbor in self.neighbors:
      neighbor.new_neighbor_count[color] += 1
      neighbor.new_neighbor_count[0] -= 1
      neighbor.new_colored_neighbors += 1

  def remove_color(self):
    for neighbor in self.neighbors:
      neighbor.new_neighbor_count[self.color] -= 1
      neighbor.new_neighbor_count[0] += 1
      neighbor.new_colored_neighbors -= 1

    self.new_color = 0

  def update_color(self):
    # Check which color type has the most neighbors.
    votes = self.neighbor_count.copy()
    if self.color > 0:
      votes[self.color] += 1.5
    new_color = np.argmax(votes[1:]) + 1

    
    if new_color != self.color and votes[new_color] > self.colored_neighbors / 2.0:
      # Update new values for this node (will become current at end of this iteration).
      self.new_color = new_color

      # Update neighbor count for neighboring nodes.
      for neighbor in self.neighbors:
        neighbor.new_neighbor_count[self.color] -= 1
        neighbor.new_neighbor_count[new_color] += 1 
        if self.color == 0:
          neighbor.new_colored_neighbors += 1

      return True

    return False

  def complete_iteration(self):
    self.color = self.new_color
    self.neighbor_count = self.new_neighbor_count.copy()
    self.colored_neighbors = self.new_colored_neighbors

  def reset(self, num_colors):
    # Set current values.
    self.color = 0
    self.neighbor_count = np.zeros(num_colors + 1)
    self.neighbor_count[0] = len(self.neighbors)
    self.colored_neighbors = 0

    # New values (updated at each iteration).
    self.new_color = self.color
    self.new_neighbor_count = self.neighbor_count.copy()
    self.new_colored_neighbors = self.colored_neighbors

  def check_node(self, where=""):
    print(where)
    if np.sum(self.neighbor_count[1:]) != self.colored_neighbors:
      print(f'uh oh: {np.sum(self.neighbor_count[1:])}, {self.colored_neighbors}')
      sum = 0
      for neighbor in self.neighbors:
        sum += int(neighbor.color > 0)
      print(f'real: {sum}')

    if (np.sum(self.neighbor_count) != len(self.neighbors)):
      print(f'extra uh oh')


############################    
### SIMULATION FUNCTIONS ###
############################

def sim(nodes, seeds):
#   print(f'Seeds: {seeds}')
  # List of (index of color, labels of nodes to seed for this color)
  indexed_seeds = [(idx, seeds[key]) for (idx, key) in enumerate(seeds.keys(), 1)]
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

  total_counts = np.zeros(num_colors + 1)
  for node in nodes.values():
    total_counts[node.color] += 1

  return {color : total_counts[idx] for (idx, color) in enumerate(seeds.keys(), 1)}


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
  for (color, seed_labels) in indexed_seeds:
    for node_label in seed_labels:
      node = nodes[node_label]
      if node.color > 0:
        conflicts.add(node)
      else:
        # print(f'seeded node {node_label} with color {color}')
        node.init_color(color)

  # Resolve conflicts by setting node to have no color.
  for node in conflicts:
    node.remove_color()

  for node in nodes.values():
    node.complete_iteration()


def complete_iteration(nodes):
  for node in nodes.values():
    node.complete_iteration()

def iterate(nodes):
  converged = True

  # First update colors according to voting scheme.
  for node in nodes.values():
    if node.update_color():
      converged = False
  
  # Set current values to new values.
  for node in nodes.values():
    node.complete_iteration()

  return converged