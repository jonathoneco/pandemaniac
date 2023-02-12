import networkx as nx
import numpy as np
import itertools
from tqdm import tqdm
import json
import sklearn.cluster as cluster
from collections import Counter


def get_graph_from_file(filename):
    with open(filename, "r") as graphjson:
        adj_list = json.load(graphjson)
    G = nx.Graph()
    for u in adj_list.keys():
        G.add_node(u)
    for u, neighbors in adj_list.items():
        G.add_edges_from([(u, neighbor) for neighbor in neighbors])
    return G


def get_centralities(graph):
    return [nx.degree_centrality(graph), nx.betweenness_centrality(graph), nx.closeness_centrality(graph)]

def get_clustered_nodes(G, n_clusters=2):
    adj_matrix = nx.adjacency_matrix(G)
    X = np.array(adj_matrix.todense())

    kmeans = cluster.KMeans(n_clusters=n_clusters)
    kmeans.fit(X)

    cluster_labels = kmeans.labels_

    # Get a dictionary that maps cluster labels to node indices
    cluster_dict = dict(zip(G.nodes(), cluster_labels))

    # Count the number of nodes in each cluster
    cluster_counts = Counter(cluster_labels)

    # Get the label of the largest cluster
    largest_cluster_label = max(cluster_counts, key=cluster_counts.get)

    # Get the nodes that belong to the largest cluster
    return [node for node, label in cluster_dict.items() if label == largest_cluster_label]
