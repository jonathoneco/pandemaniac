from utils import *
import optimized_sim
from strategies import *
import concurrent.futures

def main():
    # Setup Graph
    file_name = "sample_graphs/J.5.1.json"
    G = get_graph_from_file("sample_graphs/J.5.1.json")
    adj_list = nx.to_dict_of_lists(G)
    splitname = file_name.split('.')
    num_seeds = int(splitname[1])
    if splitname[0][-1] == "J":
        n_colors = 3
    else:
        n_colors = 2
    

    print("Executing 3 strategies")

    # Run each strategy on graph, returning the top seedings.
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future1 = executor.submit(genetic_strat, G, num_seeds, n_colors)
        future2 = executor.submit(centrality_strat, G, num_seeds, n_colors)
        future3 = executor.submit(clustered_centrality_strat, G, num_seeds, n_colors)
        results = [future.result() for future in [future1, future2, future3]]
    seedings = []
    for strategy_result in results:
        seedings.extend(strategy_result)

    for i in range(len(seedings)):
        seedings[i] = frozenset(seedings[i])
    seedings = np.array(seedings)
    # Pit them against eachother
    num_agents = 2
    point_values = [20, 15, 12, 9, 6, 4, 2, 1, 0]
    combinations = itertools.combinations(seedings, num_agents)

    beats = {seeds : 0 for seeds in seedings}
    idx_to_seeds = {i : seedings[i] for i in range(len(seedings))}
    seeds_to_idx = {seedings[i] : i for i in range(len(seedings))}

    nodes = optimized_sim.create_nodes(adj_list)
    print("Pitting final seeds against eachother")
    for strats in combinations:
        comp_seeds = {seeds_to_idx[strat] : strat for strat in strats}
        scores = list(optimized_sim.sim(nodes, comp_seeds))
        scores = np.flip(np.argsort(scores))
        for idx in scores:
            beats[strats[idx]] += point_values[idx] if num_agents > 2 else 1
    
    print("outputting nodes")
    scores = list(beats.values())
    percentile_90 = np.percentile(scores, 90)
    indices = np.argwhere(scores == percentile_90)

    chosen_ones = seedings[indices]

    output_seeds(chosen_ones, file_name)


    

        







if __name__ == '__main__':
    main()