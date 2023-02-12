from collections import Counter, OrderedDict
from copy import deepcopy
from random import randint
import numpy as np

################################
### NODE CLASS AND FUNCTIONS ###
################################

class Node:

  def __init__(self, neighbors):
    self.neighbors = neighbors

    # Set current values.
    self.color = 0
    self.neighbor_count = np.array([])
    self.colored_neighbors = 0

    # New values (updated at each iteration).
    self.new_color = self.color
    self.new_neighbor_count = self.neighbor_count
    self.new_colored_neighbors = self.colored_neighbors

  def init_color(self, color):
    self.color = color

    for neighbor in self.neighbors:
      neighbor.neighbor_count[color] += 1
      neighbor.colored_neighbors += 1

  def remove_color(self):
    for neighbor in self.neighbors:
      neighbor.neighbor_count[self.color] -= 1
      neighbor.colored_neighbors -= 1

    self.color = 0

  def update_color(self):
    # Check which color type has the most neighbors.
    votes = self.neighbor_count
    if self.color > 0:
      votes[self.color] += 1.5
    new_color = np.argmax(votes)

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
    self.neighbor_count = self.new_neighbor_count
    self.colored_neighbors = self.new_colored_neighbors

  def reset(self, num_colors):
    # Set current values.
    self.color = 0
    self.neighbor_count = np.zeros(num_colors + 1)
    self.neighbor_count[0] = len(self.neighbors)
    self.colored_neighbors = 0

    # New values (updated at each iteration).
    self.new_color = self.color
    self.new_neighbor_count = self.neighbor_count
    self.new_colored_neighbors = self.colored_neighbors
    
############################    
### SIMULATION FUNCTIONS ###
############################

def sim(nodes, seeds):
  idx_to_color = {(idx+1) : color for (idx, color) in enumerate(seeds.keys())}
  idx_to_seeds = {(idx+1) : seeds[color] for (idx, color) in enumerate(seeds.keys())}
  num_colors = len(idx_to_color)

  reset_nodes(nodes, num_colors)
  seed_nodes(nodes, idx_to_seeds)
  max_rounds = randint(100, 200)
  iter = 0
  converged = False

  while iter < max_rounds and not converged:
    converged = iterate(nodes)
    iter += 1

  total_counts = np.zeros(num_colors + 1)
  for node in nodes:
    total_counts[node.color] += 1

  return {color : total_counts[idx+1] for (idx, color) in enumerate(seeds.keys())}


def create_nodes(adj_list):
  return [Node(adj_list[node]) for node in adj_list.keys()]

def reset_nodes(nodes, num_colors):
  for node in nodes:
    node.reset(num_colors)

def seed_nodes(nodes, seeds):
  conflicts = []

  # Seed each node and keep track of conflicts.
  for color in seeds.keys():
    for node_idx in seeds[color]:
      node = nodes[node_idx]
      if node.color > 0:
        conflicts.append(node)
      else:
        node.init_color(color)
  
  # Resolve conflicts by setting node to have no color.
  for node in conflicts:
    node.remove_color()

def complete_iteration(nodes):
  for node in nodes:
    node.complete_iteration()

def iterate(nodes):
  converged = True

  # First update colors according to voting scheme.
  for node in nodes:
    if node.update_color():
      converged = False
  
  # Set current values to new values.
  for node in nodes:
    node.update_iteration()

  return converged