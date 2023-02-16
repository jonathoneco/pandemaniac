import argparse
from strategies import *
from utils import *
from optimized_sim import sim_1v1
import concurrent

tested = set()
winners = {}

def main():
    # Setup Graph
    parser = argparse.ArgumentParser(description='A simple example of argparse')
    parser.add_argument('--filename', type=str, help='Input file name')
    args = parser.parse_args()
    file_name = args.filename
    G = get_graph_from_file(file_name)
    adj_list = nx.to_dict_of_lists(G)
    splitname = file_name.split('.')
    num_seeds = int(splitname[1])

    if splitname[0][-1] == "J":
        res = label_prop_jungle_strat(G, num_seeds)
    else:
        res = monkey_monkey(file_name, 4, 4)

    print(res)

    output_seeds(res, file_name)
    

def monkey_monkey(file_name, num_workers, mins=4):
    print(mins)
    splitname = file_name.split('.')
    num_seeds = int(splitname[1])

    # Setup the graph.
    G, idx_to_label = construct_graph(file_name)
    diag = 1.5 * np.ones(G.order())
    A = nx.adjacency_matrix(G) + np.diag(diag)

    # Use degree centrality as a baseline.
    c_deg = nx.degree_centrality(G)
    sorted_deg = sorted(c_deg.keys(), key=lambda x : c_deg[x], reverse=True)
    seeds_deg = frozenset(sorted_deg[:num_seeds])

    # Compute sample space and probabilities for our baseline.
    sample_nodes = sorted_deg[:(G.order() // 2)]
    sample_probs = np.array([c_deg[node] for node in sample_nodes])
    sample_probs = sample_probs / np.sum(sample_probs)
    print(f'Meta seeds: {[idx_to_label[node] for node in seeds_deg]}')

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as monkey:
        peels = [monkey.submit(banana, A, num_seeds, seeds_deg, sample_nodes, sample_probs, mins=mins) for _ in range(num_workers)]
        concurrent.futures.wait(peels)
    # banana(A, num_seeds, seeds_deg, sample_nodes, sample_probs)

    # Export seed that works best.
    if len(winners) > 0:
        winner = max(winners, key=winners.get)
    else:
        winner = seeds_deg
    winner_labels = [idx_to_label[node] for node in winner]
    return [frozenset(winner_labels)]

def banana(A, n_seeds, meta_seeds, sample_nodes, probs, mins=4):
    start_time = datetime.now()
    while (datetime.now() - start_time).total_seconds() < mins*60:
        # print((datetime.now() - start_time).total_seconds())
        seeds = frozenset(np.random.choice(sample_nodes, n_seeds, replace=False, p=probs))

        if seeds not in tested:
            tested.add(seeds)
            monkey_score, machine_score = sim_1v1(A, seeds, meta_seeds)

            if monkey_score > machine_score:
                winners[seeds] = monkey_score
                print(f'Monkey go brr! Seed: {seeds}, Score: {monkey_score}:{machine_score}')

if __name__ == '__main__':
    main()