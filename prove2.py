import networkx as nx
import pickle
import pandas as pd
import sys
import matplotlib.pyplot as plt


if __name__ == "__main__":

    # Grafo semoplice
    F = nx.Graph()
    archi = [(0, 1),
             (0, 4),
             (1, 2),
             (1, 4),
             (2, 3),
             (3, 4),
             (3, 5)
             ]
    F.add_edges_from(archi)
    my_pos = nx.kamada_kawai_layout(F)
    nx.draw(F,
            with_labels=True,
            pos=my_pos,
            node_size=500,
            node_color='#1E78B4',
            font_color="white"
            )
    plt.savefig("simple_graph.png")
    plt.clf()

    # sys.exit()

    # Grafo sconnesso
    G = nx.Graph()
    archi = [(0, 1),
             (1, 2),
             (3, 4),
             (3, 5),
             (3, 6),
             (5, 6)
             ]
    G.add_edges_from(archi)

    my_pos = nx.kamada_kawai_layout(G)
    nx.draw_networkx_nodes(G, my_pos,
                           nodelist=[0, 1, 2],
                           node_color='#1E78B4',
                           node_size=500,)
    nx.draw_networkx_nodes(G, my_pos,
                           nodelist=[3, 4, 5, 6],
                           node_color='#FF781E',
                           node_size=500,)
    nx.draw_networkx_edges(G, my_pos)
    labels = {}
    labels[0] = 'A'
    labels[5] = 'B'
    nx.draw_networkx_labels(G, my_pos, labels, font_color='white')
    plt.axis('off')
    plt.savefig("disconnected_graph.png")  # save as png