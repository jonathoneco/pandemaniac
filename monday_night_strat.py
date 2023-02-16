import argparse
import numpy as np
from strategies import *
from utils import *
import queue
from optimized_sim import sim_1v1#, sim1v1gpu
import concurrent.futures   
# import torch
import yappi
import multiprocessing

tested = set()
N_SLEEPER = 5
# iters = tqdm(desc="iters")

def main():
    # Setup Graph
    parser = argparse.ArgumentParser(description='A simple example of argparse')
    parser.add_argument('--filename', type=str, help='Input file name')
    parser.add_argument('--drugs', type=int, help='Number of threads to use')
    args = parser.parse_args()
    file_name = args.filename
    num_threads = args.drugs

    G = get_graph_from_file(file_name)
    adj_list = nx.to_dict_of_lists(G)
    splitname = file_name.split('.')
    num_seeds = int(splitname[1])

    if splitname[0][-1] == "J":
        res = label_prop_jungle_strat(G, num_seeds)
    else:
        res = monkey_monkey(file_name, num_threads, mins=4)

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
    # sample_nodes = sample_nodes[30:]
    sample_probs = np.array([c_deg[node] for node in sample_nodes])
    sample_probs = sample_probs / np.sum(sample_probs)
    print(f'Meta seeds: {[idx_to_label[node] for node in seeds_deg]}')
    winners = dict()
    # yappi.start()
    # pool = multiprocessing.pool.Pool()
    # results = multiprocessing.Queue()
    # # prog = tqdm(desc="iters")
    # for i in range(num_workers):
    #     pool.apply_async(banana, args=(A.copy(), num_seeds, list(seeds_deg).copy(), sample_nodes.copy(), sample_probs.copy(), mins), callback=results.put)
    
    # pool.close()
    # pool.join()

    # tot_iters = 0
    # while not results.empty():
    #     cur = results.get()
    #     if cur[0] is not None:
    #         winners.update(cur[0])
    #         tot_iters += cur[1]
    # print(f"Number of iters: {tot_iters}")

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as monkey:
        try:
            peels = [monkey.submit(banana, A.copy(), num_seeds, list(seeds_deg).copy(), sample_nodes.copy(), sample_probs.copy(), mins=mins) for i in range(num_workers)]
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
    # banana(A, num_seeds, list(seeds_deg), sample_nodes, sample_probs)
    print("done")
    # yappi.stop()
    # yappi.get_func_stats().print_all()
    # yappi.get_thread_stats().print_all()
    # Export seed that works best.
    if len(winners) > 0:
        winner = max(winners, key=winners.get)
    else:
        winner = seeds_deg
    winner_labels = [idx_to_label[node] for node in winner]
    return [frozenset(winner_labels)]

def banana(A, n_seeds, meta_seeds, sample_nodes, probs, mins=4):
    start_time = datetime.now()
    # tested = set()
    # noniters = tqdm(desc="noniters")
    winners = {}
    i = 0
    while (datetime.now() - start_time).total_seconds() < mins * 60:
        # print((datetime.now() - start_time).total_seconds())
        n_sleeper = np.random.randint(1, N_SLEEPER)
        # n_sleeper = 10
        # add set to seeds
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
        # else: 
    return winners, i
            # noniters.update(1)

# def cocaine_monkey_monkey(file_name, num_workers, mins=4):
#     print(mins)
#     splitname = file_name.split('.')
#     num_seeds = int(splitname[1])

#     # Setup the graph.
#     G, idx_to_label = construct_graph(file_name)
#     diag = 1.5 * np.ones(G.order())
#     A = nx.adjacency_matrix(G) + np.diag(diag)
#     A = torch.tensor(A).float()
#     # Use degree centrality as a baseline.
#     c_deg = nx.degree_centrality(G)
#     sorted_deg = sorted(c_deg.keys(), key=lambda x : c_deg[x], reverse=True)
#     seeds_deg = frozenset(sorted_deg[:num_seeds])

#     # Compute sample space and probabilities for our baseline.
#     sample_nodes = sorted_deg[:(G.order() // 2)]
#     # sample_nodes = sample_nodes[30:]
#     sample_probs = np.array([c_deg[node] for node in sample_nodes])
#     sample_probs = sample_probs / np.sum(sample_probs)
#     print(f'Meta seeds: {[idx_to_label[node] for node in seeds_deg]}')
#     seeds_deg = torch.tensor(list(seeds_deg))
#     sample_nodes = torch.tensor(sample_nodes)
#     winners = dict()

#     with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as monkey:
#         try:
#             peels = [monkey.submit(coke, A.clone(), num_seeds, seeds_deg.clone(), sample_nodes.clone(), sample_probs.copy(), mins=mins) for i in range(num_workers)]
#             results = [future.result() for future in concurrent.futures.as_completed(peels)]
#             for cur in results:
#                 if cur is not None:
#                     winners.update(cur)

#         except KeyboardInterrupt:
#             print("KeyboardInterrupt received, shutting down thread pool")
#             # Gracefully shut down the thread pool
#             monkey.shutdown(wait=False)
#             print("Thread pool shut down")
#     # banana(A, num_seeds, list(seeds_deg), sample_nodes, sample_probs)
#     print("done")
#     # Export seed that works best.
#     if len(winners) > 0:
#         winner = max(winners, key=winners.get)
#     else:
#         winner = seeds_deg
#     winner_labels = [idx_to_label[node.item()] for node in winner]
#     return [frozenset(winner_labels)]

# def coke(A, n_seeds, meta_seeds, sample_nodes, probs, mins=4):
#     start_time = datetime.now()
#     iters = tqdm(desc="iters")
#     # noniters = tqdm(desc="noniters")
#     while (datetime.now() - start_time).total_seconds() < mins*60:
#         # print((datetime.now() - start_time).total_seconds())
#         n_sleeper = np.random.randint(1, N_SLEEPER)
#         # n_sleeper = 10
#         # add set to seeds
#         seeds = set(np.random.choice(meta_seeds, n_seeds - n_sleeper, replace=False))
#         seeds = seeds.union(np.random.choice(sample_nodes, n_sleeper, replace=False, p=probs))
#         seeds = torch.tensor(list(seeds))
#         winners = {}

#         if frozenset(seeds) not in tested:
#             tested.add(frozenset(seeds))
#             iters.update(1)
#             monkey_score, machine_score = sim1v1gpu(A, seeds, meta_seeds)

#             if monkey_score > machine_score:
#                 winners[seeds] = monkey_score
#                 print(f'Monkey found a seed! Nodes: {seeds}, Score: {monkey_score}:{machine_score}')
#         # else: 

#     return winners
            # noniters.update(1)
if __name__ == '__main__':
    
    main()