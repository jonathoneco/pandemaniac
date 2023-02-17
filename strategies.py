from utils import *
from genetic_utils import *
import networkx as nx
import numpy as np
import optimized_sim
from tqdm import tqdm
import itertools
import sklearn.cluster as cluster
from collections import Counter
from datetime import datetime
from networkx.algorithms.community import label_propagation_communities as lpc

def centrality_strat(G, n_seeds, n_colors=2, n_partitions=100):
  adj_list = nx.to_dict_of_lists(G)
  nodes = optimized_sim.create_nodes(adj_list)
  c_measures = get_centralities(G)
  seed_combos = []

  # Generate potential strategies (seed nodes).
  print('Generating potential seed combinations... centralities')
  for alpha in tqdm(np.linspace(0, 1, n_partitions)):
    for beta in np.linspace(0, 1 - alpha, n_partitions):
      weights = [alpha, beta, 1 - alpha - beta]
      seed = frozenset(choose_seed_nodes_given_weights(weights, n_seeds, G, c_measures=c_measures))

      if seed not in seed_combos:
        seed_combos.append(seed)

  # Maps a set of seed nodes to sets of seed nodes that it beats.
  beats = {seed : 0 for seed in seed_combos}
  print("pitting centralities together centralities")
  subsets = itertools.combinations(seed_combos, n_colors)
  for subset in tqdm(subsets):
    entry = {i : subset[i] for i in range(len(subset))}
    res = optimized_sim.sim(nodes, entry)
    winner = sorted(res.keys(), key=lambda x : res[x], reverse=True)[0]

    beats[seed_combos[winner]] += n_colors - 1
  print("finished pitting centralities")

  return sorted(beats.keys(), key=lambda x : beats[x], reverse=True)[:20]

def clustered_centrality_strat(G, n_seeds, n_colors=2, n_partitions=100):
    adj_matrix = nx.adjacency_matrix(G)
    adj_list = nx.to_dict_of_lists(G)
    X = np.array(adj_matrix.todense())

    kmeans = cluster.KMeans(n_clusters=n_colors)
    kmeans.fit(X)

    cluster_labels = [] if kmeans.labels_ is None else list(kmeans.labels_)
    # Get a dictionary that maps cluster labels to node indices
    cluster_dict = dict(zip(G.nodes(), cluster_labels))

    # Count the number of nodes in each cluster
    cluster_counts = Counter(cluster_labels)

    # Get the label of the largest cluster
    largest_cluster_label = max(cluster_counts, key=cluster_counts.get)

    # Get the nodes that belong to the largest cluster
    largest_cluster_nodes = [node for node, label in cluster_dict.items() if label == largest_cluster_label]

    nodes = optimized_sim.create_nodes(adj_list)
    c_measures = get_centralities(G)
    seed_combos = []

	# Generate potential strategies (seed nodes).
    print('Generating potential seed combinations... clustered')
    for alpha in tqdm(np.linspace(0, 1, n_partitions)):
        for beta in np.linspace(0, 1 - alpha, n_partitions):
            weights = [alpha, beta, 1 - alpha - beta]
            seed = frozenset(choose_seed_nodes_given_weights(weights, n_seeds, G, largest_cluster_nodes=largest_cluster_nodes, c_measures=c_measures))

            if seed not in seed_combos:
                seed_combos.append(seed)

	# Maps a set of seed nodes to sets of seed nodes that it beats.
    seeds = {i : seed_combos[i] for i in range(len(seed_combos))}
    beats = {seed : [] for seed in seed_combos}

    print("pitting against eachother clustered")
    subsets = itertools.combinations(seed_combos, n_colors)
    for subset in tqdm(subsets):
        entry = {i : subset[i] for i in range(len(subset))}
        res = optimized_sim.sim(nodes, entry)
        winner = sorted(res.keys(), key=lambda x : res[x], reverse=True)[0]

        for i in range(len(subset)):
            if i != winner:
                beats[entry[winner]].append([entry[i]])
    print("finished pitting seeds clustered")
    return sorted(beats.keys(), key=lambda x : len(beats[x]), reverse=True)[:20]

def genetic_strat(G, n_seeds, n_colors=2, n_generations=5, pop_size=30, n_parents=4, mutations_div = 3):
    old_parents = np.empty(1)
    num_same = 0
    print("gen first pop")
    population = [np.random.choice(list(G.nodes), n_seeds, replace=False) for _ in range(pop_size)]
    nodes = optimized_sim.create_nodes(nx.to_dict_of_lists(G))
    n_mutations = int(n_seeds / mutations_div)
    print("doing generations")
    for i in tqdm(range(n_generations)):
        print("generatioN!")
        fitness = calc_pop_fitness(population, nodes, n_colors)
        parents = select_mating_pool(population, fitness, n_parents, n_seeds=n_seeds)
        old_parents = parents
        offspring = crossover(parents, pop_size-n_parents, n_seeds=n_seeds)
        offspring = mutation(offspring, G, n_mutations)
        population = []
        population.extend(parents.astype(int).astype(str))
        population.extend(offspring.astype(int).astype(str))
    fitness = calc_pop_fitness(population, nodes, n_colors)
    best_fitness = np.flip(np.argsort(fitness))
    population = np.array(population)
    winning_strategies = population[best_fitness[:20]]
    print("finished generations")
    # for i in range(len(winning_strategies)):
    #    winning_strategies[i] = frozenset(winning_strategies[i])
    return winning_strategies

def label_prop_jungle_strat(file_name, n_seeds):
    G = get_graph_from_file(file_name)
    communities = lpc(G)
    communities_list = [list(community) for community in communities]

    close_community = None
    close_community_diff = 9999999
    for community in communities_list:
        if np.abs(len(community) - n_seeds) < close_community_diff:
            close_community = community
            close_community_diff = np.abs(len(community) - n_seeds)


    seeds = []
    degrees = G.degree(close_community)
    seeds = []
    if len(close_community) >= n_seeds:
        for _ in range(50):
            seeds.append(np.random.choice(close_community, n_seeds, replace=False))
    else:
        diff = len(seeds) - n_seeds
        for _ in range(50):
            seed = []
            seed.extend(list(dict(degrees).keys()))
            seed.extend(np.random.choice((key for (key, value) in dict(G.degree()).items() if value > 0), diff, replace=False))
            seeds.append(seed)
        
    return seeds

def super_secret_strategy(G, n_seeds):
    curr_time = datetime.now()

    c_deg = dict(G.degree())
    nodes = optimized_sim.create_nodes(nx.to_dict_of_lists(G))
    deg_nodes = sorted(c_deg.keys(), key=lambda x : c_deg[x], reverse=True)[:n_seeds]
    #   print(f'Degree nodes: {deg_nodes}')

    wins = {}
    previously_tried = set()

    progress_bar = tqdm(total=3.5*60)

    while (datetime.now() - curr_time).total_seconds() < 3.5*60:
        tqdm.update(progress_bar, (datetime.now() - curr_time).total_seconds())
        seed = frozenset(np.random.choice(G.nodes(), n_seeds, replace=False))
        
        if seed not in previously_tried:
            rand, deg = score_seeds_opt(seed, deg_nodes, nodes)
            previously_tried.add(seed)
        if rand > deg:
            wins[seed] = rand
            print(f'{seed} beat degrees')
    #   print(wins)
    rand_seeds = list(wins.keys())
    beats = {seeds : 0 for seeds in rand_seeds}
    
    seeds_to_idx = {rand_seeds[i] : i for i in range(len(rand_seeds))}

    combinations = itertools.combinations(rand_seeds, 2)
    print("Pitting final seeds against eachother")
    for strats in combinations:
        comp_seeds = {seeds_to_idx[strat] : strat for strat in strats}
        scores = list(optimized_sim.sim(nodes, comp_seeds))
        scores = np.flip(np.argsort(scores))
        for idx in scores:
            beats[strats[idx]] += 1

    sorted_beats = sorted(beats.items(), key=lambda item: item[1], reverse=True)
    if len(sorted_beats) == 0:
        return [frozenset(deg_nodes)]
    seeding = [sorted_beats[0][0]]
    return seeding

    


            