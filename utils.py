import networkx as nx
import optimized_sim
import numpy as np
import itertools
from tqdm import tqdm
import json
import sklearn.cluster as cluster
from collections import Counter
import sim


def get_graph_from_file(filename):
    with open(filename, "r") as graphjson:
        adj_list = json.load(graphjson)
    G = nx.Graph()
    for u in adj_list.keys():
        G.add_node(u)
    for u, neighbors in adj_list.items():
        G.add_edges_from([(u, neighbor) for neighbor in neighbors])
    return G


def get_centralities(graph):
    return [nx.degree_centrality(graph), nx.betweenness_centrality(graph), nx.closeness_centrality(graph)]

def get_clustered_nodes(G, n_clusters=2):
    adj_matrix = nx.adjacency_matrix(G)
    X = np.array(adj_matrix.todense())

    kmeans = cluster.KMeans(n_clusters=n_clusters)
    kmeans.fit(X)

    cluster_labels = kmeans.labels_

    # Get a dictionary that maps cluster labels to node indices
    cluster_dict = dict(zip(G.nodes(), cluster_labels))

    # Count the number of nodes in each cluster
    cluster_counts = Counter(cluster_labels)

    # Get the label of the largest cluster
    largest_cluster_label = max(cluster_counts, key=cluster_counts.get)

    # Get the nodes that belong to the largest cluster
    return [node for node, label in cluster_dict.items() if label == largest_cluster_label]

def choose_seed_nodes_given_weights(weights, num_seeds, graph, largest_cluster_nodes = None, c_measures = None):
    """
    Function: choose_seed_nodes_given_weights
    -----------------------------------------
    Chooses seed nodes based on the weights given.
    """
    if not c_measures:
        c_measures = get_centralities(graph)
    if not largest_cluster_nodes:
        largest_cluster_nodes = graph.nodes

    centrality = {}
    
    for node in largest_cluster_nodes:
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
    return bool((result['1'] > result['2'])) - bool((result['1'] < result['2']))

def score_seeds(seed1, seed2, adj_list):
    seeds = {"1": seed1, "2": seed2}
    # nodes = optimized_sim.create_nodes(adj_list)
    # result = optimized_sim.sim(nodes, seeds)
    result = sim.run(adj_list, seeds)
    return result

def score_seeds_opt(seed1, seed2, nodes):
    seeds = {'1': seed1, '2': seed2}
    result = optimized_sim.sim(nodes, seeds)
    return (result['1'], result['2'])
    
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
            nodes = frozenset(choose_seed_nodes_given_weights(weights, num_seeds, graph, c_measures=c_measures))

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


def output_seeds(seeds, filename, n=50):
    f = open(f'{filename}_seeds.txt', 'w')

    for i in range(n):
        for seed in seeds[i % len(seeds)]:
            for node in seed:
                f.write(f'{node}\n')

    f.close()