import argparse
import numpy as np
import networkx as nx
from strategies import *
from utils import *
from optimized_sim import sim_1v1
import concurrent.futures
import itertools
import multiprocessing

def main():
    # Setup Graph
    parser = argparse.ArgumentParser(description='A simple example of argparse')
    parser.add_argument('--filename', type=str, help='Input file name')
    parser.add_argument('--drugs', type=int, help='Number of threads to use')
    args = parser.parse_args()
    file_name = args.filename
    num_threads = args.drugs

    splitname = file_name.split('.')
    num_seeds = int(splitname[1])

    if splitname[0][-1] == "J":
        res = label_prop_jungle_strat(file_name, num_seeds)
        output_seeds(res, file_name)
    else:
        res = monkey_rr(file_name, num_seeds, num_threads)
        print(f'Winning seeds: {res}')
        output_seeds(res, file_name)


def monkey_rr(file_name, num_seeds, num_threads):
    # Setup the graph.
    G, idx_to_label = construct_graph(file_name)
    diag = 1.5 * np.ones(G.order())
    A = nx.adjacency_matrix(G) + np.diag(diag)

    # Use degree centrality as a baseline.
    degrees = dict(nx.degree(G))
    sorted_deg = sorted(degrees.keys(), key=lambda x : degrees[x], reverse=True)
    seeds_deg = frozenset(sorted_deg[:num_seeds])

    # Compute sample space and probabilities for our baseline.
    sample_nodes = sorted_deg[num_seeds:(G.order() // 2)]
    sample_probs = np.array([degrees[node] for node in sample_nodes])
    sample_probs = sample_probs / np.sum(sample_probs)
    print(f'Meta seeds: {[idx_to_label[node] for node in seeds_deg]}')
    winners = {}

    start_time = datetime.now()
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as monkey:
        try:
            peels = [monkey.submit(banana_1, A.copy(), num_seeds, seeds_deg.copy(), sample_nodes.copy())]
            for i in range(2, 5):
                peels.extend([monkey.submit(banana,
                                            A.copy(),
                                            num_seeds,
                                            list(seeds_deg),
                                            sample_nodes.copy(),
                                            sample_probs.copy(),
                                            i
                                           ) for _ in range(i)])

            results = [future.result() for future in concurrent.futures.as_completed(peels)]
            seeds_tested = 0
            for (seeds, iters) in results:
                winners.update(seeds)
                seeds_tested += iters
            print(f'Total number of seeds tested: {seeds_tested}')
        except KeyboardInterrupt:
            # Gracefully shut down the thread pool.
            print("KeyboardInterrupt received, shutting down thread pool...", end=" ")
            monkey.shutdown(wait=False)
            print("thread pool shut down.")
    print((datetime.now() - start_time).total_seconds())

    if len(winners) > 0:
        print(f'Threads completed. Monkey is pitting the top 100 seeds to the death...')
        top_seeds = sorted(winners.keys(), key=lambda x : winners[x], reverse=True)[:100]
        scores = {seed : 0 for seed in top_seeds}

        for s1, s2 in itertools.combinations(top_seeds, 2):
            s1_score, s2_score = sim_1v1(A, s1, s2)

            if s1_score > s2_score:
                scores[s1] += 1
            if s1_score < s2_score:
                scores[s2] += 1

        winner = max(scores, key=scores.get)
    else:
        print('Nothing beat degree seeds! Sometimes simple is best...')
        winner = seeds_deg

    winner_labels = [idx_to_label[node] for node in winner]
    return [frozenset(winner_labels)]


def banana_1(A, num_seeds, meta_seeds, sample_nodes, mins=3):
    start_time = datetime.now()
    winners = {}
    i = 0

    for nodes in itertools.combinations(meta_seeds, num_seeds - 1):
        for sleeper in sample_nodes:
            seed = set(nodes)
            seed.add(sleeper)
            seed = frozenset(seed)

            monkey_score, machine_score = sim_1v1(A, seed, meta_seeds)
            if monkey_score > machine_score:
                winners[seed] = monkey_score

            i += 1
        
        if (datetime.now() - start_time).total_seconds() > (60 * mins):
            break
    
    return winners, i

def banana(A, n_seeds, meta_seeds, sample_nodes, sample_probs, n_sleepers, mins=3):
    start_time = datetime.now()
    tested = set()
    winners = {}
    i = 0
    num_same = 0
    while (datetime.now() - start_time).total_seconds() < (60 * mins):
        num_same = 0
        for _ in range(500):
            seed = set(np.random.choice(meta_seeds, n_seeds - n_sleepers, replace=False))
            seed = seed.union(np.random.choice(sample_nodes, n_sleepers, replace=False, p=sample_probs))
            seed = frozenset(seed)
            
            if seed not in tested:
                tested.add(seed)
                i += 1
                monkey_score, machine_score = sim_1v1(A, seed, meta_seeds)

                if monkey_score > machine_score:
                    winners[seed] = monkey_score
            else: 
                num_same += 1

        if num_same > 100:
            n_sleepers += 1

    return winners, i
            
if __name__ == '__main__':
    main()
    