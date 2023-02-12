import networkx as nx
import optimized_sim
import numpy as np
import itertools
from tqdm import tqdm
import json

def get_graph_from_file(filename):
    with open(filename, "r") as graphjson:
        adj_list = json.load(graphjson)
    G = nx.Graph()
    for u, neighbors in adj_list.items():
        G.add_edges_from([(u, neighbor) for neighbor in neighbors])
    return G


def get_centralities(graph):
    return [nx.degree_centrality(graph), nx.betweenness_centrality(graph), nx.closeness_centrality(graph)]

def choose_seed_nodes_given_weights(weights, num_seeds, graph, c_measures = None):
    """
    Function: choose_seed_nodes_given_weights
    -----------------------------------------
    Chooses seed nodes based on the weights given.
    """
    if not c_measures:
        c_measures = get_centralities(graph)
    centrality = {}
    
    for node in graph.nodes:
        centrality[node] = c_measures[0][node] * weights[0] + c_measures[1][node] * weights[1] + c_measures[2][node] * weights[2]
    
    return sorted(centrality, key=centrality.get, reverse=True)[:num_seeds]


def score_strat(weights, num_seeds, graph, comp_nodes, adj_list):
    seeds = choose_seed_nodes_given_weights(weights, num_seeds, graph)
    comp_nodes["Modelo Time"] = seeds
    nodes = optimized_sim.create_nodes(adj_list)
    return optimized_sim.sim(nodes, comp_nodes)["Modelo Time"]

def gen_weights(num_seeds, graph, comp_nodes={}):
    """
    Function: gen_weights
    -------------------
    Generates a score for a given strategy.
    """
    adj_list = nx.to_dict_of_lists(graph)

    ret = dict()
    # for i from 0 to 1 in increments of 0.05
    for i in np.linspace(0, 1, 21):
        for j in np.linspace(0, 1 - i, 21):
          k = 1 - i - j
          ret[(i, j, k)] = score_strat([i, j, k], num_seeds, graph, comp_nodes, adj_list)

def score_comp_seeds(seed1, seed2, adj_list):
    seeds = {"1": seed1, "2": seed2}
    nodes = optimized_sim.create_nodes(adj_list)
    result = optimized_sim.sim(nodes, seeds)
    return (result['1'] > result['2']) - (result['1'] < result['2'])

def score_seeds(seed1, seed2, adj_list):
    seeds = {"1": seed1, "2": seed2}
    nodes = optimized_sim.create_nodes(adj_list)
    result = optimized_sim.sim(nodes, seeds)
    return result

def compete(num_seeds, graph, n_partitions):
    nodes_combos = []
    # networkx graph to adjacency list
    adj_list = nx.to_dict_of_lists(graph)

    # Centralities
    c_measures = get_centralities(graph)

    # Generate potential strategies (seed nodes).
    print('Generating potential seed combinations...')
    for alpha in tqdm(np.linspace(0, 1, n_partitions)):
        for beta in np.linspace(0, 1 - alpha, n_partitions):
            weights = [alpha, beta, 1 - alpha - beta]
            nodes = frozenset(choose_seed_nodes_given_weights(weights, num_seeds, graph, c_measures))

            if nodes not in nodes_combos:
                nodes_combos.append(nodes)

    # Maps a set of seed nodes to sets of seed nodes that it beats.
    beats = {nodes : [] for nodes in nodes_combos}

    # Test each pair against the others.
    print('Pitting seeds to the death...')
    combinations = itertools.combinations(nodes_combos, 2)
    for strat1, strat2 in tqdm(combinations):
        if strat2 not in beats[strat1] and strat1 not in beats[strat2]:
            # Pit the two strategies against each other. Probabilistically
            # say the winner also beats strategies that the loser beats.
            res = score_comp_seeds(list(strat1), list(strat2), adj_list)

            if   res ==  1: beats[strat1].append(strat2)
            elif res == -1: beats[strat2].append(strat1)
            elif res ==  0: continue#print(f'Tie between {strat1} and {strat2}')

    return sorted(beats.keys(), key=lambda x : len(beats[x]), reverse=True)