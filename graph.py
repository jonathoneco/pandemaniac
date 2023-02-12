import networkx as nx
import numpy as np
import sys
from utils import *

# if main is called, then we are running this file directly
if __name__ == "__main__":
    # grab argument filename
    filename = sys.argv[1]
    # get graph from file
    G = get_graph_from_file(filename)
    # get centralities
    c_measures = get_centralities(G)
    # get largest cluster nodes
    largest_cluster_nodes = get_clustered_nodes(G)
    # get seed nodes
    centralities = [nx.degree_centrality(G), nx.betweenness_centrality(G), nx.closeness_centrality(G)]
    json.dump(centralities, sys.stdout)

#         for i in range(len(c_measures)):
