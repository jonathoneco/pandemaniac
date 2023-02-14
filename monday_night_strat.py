import argparse
from strategies import *
from utils import *


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
        res = super_secret_strategy(G, num_seeds)

    print(res)

    output_seeds(res, file_name)
    

if __name__ == '__main__':
    main()