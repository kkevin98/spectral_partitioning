import networkx as nx
import pickle
import numpy as np
import matplotlib.pyplot as plt
# import pygraphviz as pgv
from networkx.generators.random_graphs import fast_gnp_random_graph
from networkx.classes.function import number_of_selfloops
from my_network_lib import remove_self_edges, spectral_partition_basic


# Per creare un grafo casuale
test_graph = fast_gnp_random_graph(2, 1)

'''
# Per leggere un edgelist (mio)
test_graph = nx.read_edgelist("test_10_nodi.edgelist")
if not nx.is_connected(test_graph):
    print("Creo un nuovo grafo, quello che mi hai dato non è connesso!!")
    test_graph = fast_gnp_random_graph(10, .5)
    nx.write_edgelist(test_graph, "test_10_nodi.edgelist")
    

# Per mostrare e salvare il grafo in ingresso sotto forma di png
nx.draw(test_graph, with_labels=True)
plt.savefig("mygraph.png")
plt.clf()
'''

# Questioni di debug sul grafo in ingresso
print("Prima del clustering il grafo ha archi:\n", test_graph.edges)
print('Il grafo di test ha: ', test_graph.number_of_edges(), ' archi')
print('Il grafo di test ha: ', test_graph.number_of_nodes(), ' nodi')
print('Il grafo di test ha: ', number_of_selfloops(test_graph), ' self-edges')


# Per trasformare l' edgelist in un grafo da dare in pasto all'algoritmo (mio)
# Trasformo i nodi da città a int così da poter usare l'algoritmo, mi torna una copia da usare per l'algoritmo
working_graph = nx.convert_node_labels_to_integers(test_graph)
# Per mostrare la mappatura tra nomi di città e int
mapped_vertex = dict(couple for couple in zip(nx.nodes(working_graph), nx.nodes(test_graph)))
print('Il working_graph ha: ', working_graph.number_of_edges(), ' archi')
print('Il working_graph ha: ', working_graph.number_of_nodes(), ' nodi')
print('Il working_graph ha: ', number_of_selfloops(working_graph), ' self-edges')


# Questioni di debug per mostrare la mappatura tra città e int
print("Mappatura tra città e int:\n", mapped_vertex)


# Per avviare l'algoritmo vero e proprio
spectral_partition_basic(working_graph, 1, 1)


# Per rimettere i nomi delle città al posto degli int nel grafo risultato della partizione
nx.relabel_nodes(working_graph, mapped_vertex, copy=False)


# Questioni di debug sul grafo in uscita
print("Dopo il clustering il grafo ha archi:\n", working_graph.edges)
print('Il grafo di test ha: ', working_graph.number_of_edges(), ' archi')
print('Il grafo di test ha: ', working_graph.number_of_nodes(), ' nodi')
print('Il grafo di test ha: ', number_of_selfloops(working_graph), ' self-edges')

'''
# Per salvare sottoforma di egelist il grafo di uscita (mio)
nx.write_edgelist(working_graph, "test_10_nodi_res.edgelist")


# Per mostrare e salvare il grafo in uscita sotto forma di png
nx.draw(working_graph, with_labels=True)
plt.savefig("mygraph_res.png")
plt.clf()
'''