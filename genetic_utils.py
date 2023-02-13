import numpy as np
import sim
from utils import *
import networkx as nx
from tqdm import tqdm

def calc_pop_fitness(pop, nodes, n_colors, pop_size=30):
    point_values = [20, 15, 12, 9, 6, 4, 2, 1, 0]
    popsets = [frozenset(elem) for elem in pop]
    combinations = itertools.combinations(popsets, n_colors)
    beats = {seeds : 0 for seeds in popsets}
    idx_to_seeds = {i : popsets[i] for i in range(len(popsets))}
    seeds_to_idx = {popsets[i] : i for i in range(len(popsets))}

    for strats in combinations:
        comp_seeds = {seeds_to_idx[strat] : strat for strat in strats}
        scores = list(optimized_sim.sim(nodes, comp_seeds))
        scores = np.flip(np.argsort(scores))
        for idx in scores:
            beats[strats[idx]] += point_values[idx] if n_colors > 2 else 1

    fitness = list(beats.values())
    return fitness

def select_mating_pool(pop, fitness, num_parents, n_seeds=5):
    parents = np.zeros((num_parents, n_seeds))
    for parent_num in range(num_parents):
        max_fitness_idx = np.argmax(fitness)
        parents[parent_num] = pop[max_fitness_idx]
        fitness[max_fitness_idx] = -999999999
    return parents

def crossover(parents, offspring_size, n_seeds=5, num_parents=2):
    offspring = np.empty((offspring_size, n_seeds))
    for k in range(offspring_size):
        parent1_idx, parent2_idx = np.random.choice(num_parents, 2, replace=False)
        parents_seeds = np.unique(np.concatenate((parents[parent1_idx], parents[parent2_idx])))
        test = np.random.choice(parents_seeds, n_seeds, replace=False)
        offspring[k] = test
    return offspring

def mutation(offspring_crossover, G, num_mutations):
    for idx in range(offspring_crossover.shape[0]):
        while True:
            choice = np.random.choice(G.nodes, num_mutations, replace=False).astype(int)
            if not np.isin(choice, offspring_crossover[idx]).any():
                offspring_crossover[idx, :num_mutations] = choice
                break
    return offspring_crossover


