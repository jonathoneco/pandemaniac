import numpy as np
import networkx as nx
import random
import matplotlib.pyplot as plt

def preferential_attachment_model(T):
    # Initialize the graph with two nodes and one edge
    G = nx.Graph()
    G.add_node(0)
    G.add_node(1)
    G.add_edge(0, 1)
    
    # Keep track of the degrees of each node
    degrees = [1, 1]
    
    # Add T-2 new nodes
    for t in range(2, T):
        # Compute the probabilities of connecting to each existing node
        probs = np.array(degrees) / np.sum(degrees)
        
        # Choose a node to connect to based on the probabilities
        chosen_node = np.random.choice(range(t), p=probs)
        
        # Add the new node and connect it to the chosen node
        G.add_node(t)
        G.add_edge(t, chosen_node)
        
        # Update the degrees of the chosen node and the new node
        degrees.append(1)
        degrees[chosen_node] += 1
    
    # Return the graph and the list of degrees
    return G, degrees

def configuration_model(k):
    n = len(k)
    stubs = []
    for i in range(n):
        for j in range(k[i]):
            stubs.append(i)
    random.shuffle(stubs)
    
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)
    for i in range(0, len(stubs), 2):
        G.add_edge(stubs[i], stubs[i + 1])
        
    return G