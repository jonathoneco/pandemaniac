import argparse
import numpy as np
import networkx as nx
from strategies import *
from utils import *
from optimized_sim import sim_1v1
import concurrent.futures   
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
    else:
        res = monkey_rr(file_name, num_seeds, num_threads)

    print(res)
    output_seeds(res, file_name)


def monkey_rr(file_name, num_workers, mins=4):
    splitname = file_name.split('.')
    num_seeds = int(splitname[1])

    # Setup the graph.
    G, idx_to_label = construct_graph(file_name)
    diag = 1.5 * np.ones(G.order())
    A = nx.adjacency_matrix(G) + np.diag(diag)

    # Use degree centrality as a baseline.
    degrees = dict(nx.degree(G))
    sorted_deg = sorted(degrees.keys(), key=lambda x : degrees[x], reverse=True)
    seeds_deg = frozenset(sorted_deg[:num_seeds])

    # Compute sample space and probabilities for our baseline.
    sample_nodes = sorted_deg[:(G.order() // 2)]
    sample_probs = np.array([degrees[node] for node in sample_nodes])
    sample_probs = sample_probs / np.sum(sample_probs)
    print(f'Meta seeds: {[idx_to_label[node] for node in seeds_deg]}')
    winners = dict()
    start_time = datetime.now()
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as monkey:
        try:
            peels = []
            for i in range(1, 5):
                peel = [monkey.submit(banana, A.copy(), num_seeds, list(seeds_deg).copy(), sample_nodes.copy(), sample_probs.copy(), n_sleeper=i, mins=mins) for j in range(i)]
                peels.extend(peel)
            results = [future.result() for future in concurrent.futures.as_completed(peels)]
            total_iter = 0
            for cur in results:
                if cur[0] is not None:
                    winners.update(cur[0])
                    total_iter += cur[1]
            print(f"total_iters = {total_iter}")


        except KeyboardInterrupt:
            print("KeyboardInterrupt received, shutting down thread pool")
            # Gracefully shut down the thread pool
            monkey.shutdown(wait=False)
            print("Thread pool shut down")
    print((datetime.now()-start_time).total_seconds())
    print("done")

    if len(winners) > 0:
        winner = max(winners, key=winners.get)
    else:
        winner = seeds_deg
    winner_labels = [idx_to_label[node] for node in winner]
    return [frozenset(winner_labels)]


def banana(A, n_seeds, meta_seeds, sample_nodes, probs, n_sleeper=0, mins=4):
    start_time = datetime.now()
    tested = set()
    winners = {}
    i = 0
    num_same = 0
    while (datetime.now() - start_time).total_seconds() < (mins * 60):
        num_same = 0
        seeds = set(np.random.choice(meta_seeds, n_seeds - n_sleeper, replace=False))
        seeds = seeds.union(np.random.choice(sample_nodes, n_sleeper, replace=False, p=probs))
        seeds = frozenset(seeds)
        
        if seeds not in tested:
            tested.add(seeds)
            i += 1
            # prog.update(1)
            monkey_score, machine_score = sim_1v1(A, seeds, meta_seeds)

            if monkey_score > machine_score:
                winners[seeds] = monkey_score
                # print(f'Monkey found a seed! Nodes: {seeds}, Score: {monkey_score}:{machine_score}')
        else: 
            num_same += 1
            if num_same > 100:
                n_sleeper += 1
    return winners, i
            # noniters.update(1)
            
if __name__ == '__main__':
    main()
    