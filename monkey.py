import argparse
import concurrent.futures
from utils import *
from datetime import datetime
from tqdm import tqdm

### GLOBAL VARIABLES (will be touched by threads) ###
tested  = set()
winners = {}

def banana(G, n_seeds, meta_seeds, sample_space, probs, mins=4):
    curr_time = datetime.now()
    nodes = optimized_sim.create_nodes(nx.to_dict_of_lists(G))
    iter = 0

    while (datetime.now() - curr_time).total_seconds() < mins*60:
        seed = frozenset(np.random.choice(sample_space, n_seeds, replace=False, p=probs))

        if seed not in tested:
            tested.add(seed)
            monkey_score, machine_score = score_seeds_opt(seed, meta_seeds, nodes)

            if monkey_score > machine_score:
                winners[seed] = monkey_score
                print(f'Monkey go brr! Seed: {seed}, Score: {monkey_score}:{machine_score}')



def main():
    parser = argparse.ArgumentParser(description='A simple example of argparse')
    parser.add_argument('--banana', type=str, help='Input file name')
    parser.add_argument('--drugs', type=int, help='Number of threads to use')
    args = parser.parse_args()
    file_name = args.banana
    num_workers = args.drugs

    # Setup the graph.
    G = get_graph_from_file(file_name)
    adj_list = nx.to_dict_of_lists(G)
    splitname = file_name.split('.')
    num_seeds = int(splitname[1])

    # Pre-compute highest degree nodes (or whatever metric we want to use)
    # as well as probabilities of selection for each node.
    probs = np.array([node[1] for node in G.degree]) / (2 * G.number_of_edges())
    degs = [x[0] for x in sorted(G.degree, key=lambda x: x[1], reverse=True)]
    deg_seeds = degs[:num_seeds]
    sample_space = degs[:(G.order() // 2)]
    probs = np.array([G.degree[node] for node in sample_space])
    probs = probs / np.sum(probs)

    print(f'Meta seeds: {deg_seeds}')

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as monkey:
        peels = [monkey.submit(banana, G, num_seeds, deg_seeds, sample_space, probs) for _ in range(num_workers)]
        concurrent.futures.wait(peels)

    # Export seed that works best.
    if len(winners) > 0:
        winner = max(winners, key=winners.get)
    else:
        winner = frozenset(deg_seeds)

    print(f'Seeds tested: {len(tested)}')
    print(f'Winner: {winner}')

if __name__ == '__main__':
    main()