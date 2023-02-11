import sim
import networkx as nx
import numpy as np
import itertools
from utils import *
from tqdm import tqdm

def compete(num_seeds, graph, n_partitions):
    nodes_combos = []
    
    # Generate potential strategies (seed nodes).
    print('Generating potential seed combinations...')
    for alpha in np.linspace(0, 1, n_partitions):
        for beta in np.linspace(0, 1 - alpha, n_partitions):
            weights = [alpha, beta, 1 - alpha - beta]
            nodes = choose_seed_nodes_given_weights(weights, num_seeds, graph)

            if nodes not in nodes_combos:
                nodes_combos.append(nodes)

    # Maps a set of seed nodes to sets of seed nodes that it beats.
    beats = {nodes : [] for nodes in nodes_combos}

    # Test each pair against the others.
    print('Pitting seeds to the death...')
    for strat1, strat2 in tqdm(itertools.combinations(nodes_combos, 2)):
        if strat2 not in beats[strat1] and strat1 not in beats[strat2]:
            # Pit the two strategies against each other. Probabilistically
            # say the winner also beats strategies that the loser beats.
            res = score_comp_seeds(strat1, strat2)

            if   res ==  1: beats[strat1].append(strat2)
            elif res == -1: beats[strat2].append(strat1)
            
    return sorted(beats.keys(), key=len(beats.values()))[0]