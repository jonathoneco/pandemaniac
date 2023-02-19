import argparse
import numpy as np
import networkx as nx
from strategies import *
from utils import *
from optimized_sim import sim_1v1
import concurrent.futures
import itertools
import queue

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
    sample_nodes = frozenset(sorted_deg[:(G.order() // 2)])

    winners = {}
    tested = set()
    Q = queue.PriorityQueue()
    Q.put((0, seeds_deg))
    currs = set()
    #curr_seeds = seeds_deg
    start_time = datetime.now()

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as monkey:
        try:
            while (datetime.now() - start_time).total_seconds() < 240:
                # Launch threads permuting nodes for the current set of seed nodes.
                if Q.empty():
                    curr_seeds = frozenset(np.random.choice(list(G.nodes), num_seeds, replace=False))
                else:
                    _, curr_seeds = Q.get()
                print(f'Now testing: {curr_seeds}')

                treats = [monkey.submit(
                    banana, 
                    A.copy(),
                    seeds_deg.copy(),
                    curr_seeds.copy(), 
                    to_remove, 
                    sample_nodes.difference(curr_seeds), 
                    tested.copy()
                ) for to_remove in curr_seeds]
                peels = [peel.result() for peel in concurrent.futures.as_completed(treats)]

                # Update the winners and tested set given what each thread returns.
                for (scores, tests) in peels:
                    tested = tested.union(tests)
                    winners.update(scores)

                    for (seed, score) in scores.items():
                        if seed not in currs:
                            Q.put((-1 * score, seed))
                            currs.add(seed)


        except KeyboardInterrupt:
            # Gracefully shut down the thread pool.
            print('KeyboardInterrupt received, shutting down thread pool...', end=' ')
            monkey.shutdown(wait=False)
            print('done.')

    if len(winners) > 0:
        print(f'Monkey is done eating bananas. Now pitting the top 100 seeds to the death...')
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

def banana(A, baseline_seeds, curr_seeds, to_remove, sample_nodes, tested):
    removed = curr_seeds.difference([to_remove])
    winners = {}

    for node in sample_nodes:
        new_seeds = removed.union([node])

        if new_seeds not in tested:
            tested.add(new_seeds)
            new_score, baseline_score = optimized_sim.sim_1v1(A, new_seeds, baseline_seeds)

            if new_score > baseline_score:
                winners[new_seeds] = new_score

    return winners, tested
  
            
if __name__ == '__main__':
    main()
    