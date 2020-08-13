import networkx as nx
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
from networkx.generators.random_graphs import fast_gnp_random_graph
from networkx.algorithms.components import connected_components
# from my_network_lib import spectral_partition
from networkx.algorithms.cuts import cut_size
from networkx.drawing.nx_agraph import (
    to_agraph,
    write_dot,
)
import pygraphviz as pgv
from networkx.classes.function import to_directed



a = np.array([[1.0,2.0,3.0],[4.0,5.0,6.0],[0.0,0.0,1.0]])
print("Pre-ordinamento:\n", a)
b = np.sort(a.view('f8, f8, f8'), order=['f1'], axis=0).view(np.float64)
# originale: a = np.sort(a.view('i8,i8,i8'), order=['f1'], axis=0).view(np.int)
# ultima view appesa per trasformare il tipo degli elementi da void a int
# è np.sort() che mi torna una copia dell'array!!
print("a: ", a.dtype.name)
print("b: ", b.dtype.name)
print("Post-ordinamento a:\n", a)
print("Post-ordinamento b:\n", b)

insieme = set(b[:2, 0].flat)
print("insieme: ", insieme)

'''------------------------------------------------------------------------------------------------------'''

good_graph = nx.path_graph(10)
# nx.write_edgelist(good_graph, "grafo_di_test", data=['color','weight'])
# nx.draw(good_graph, with_labels=True)
# plt.savefig("test.png")
# plt.clf()

'''-------------------------------------------------------------------------------------------------------'''

test_graph = fast_gnp_random_graph(547, .001)
'''
# test_graph = nx.read_edgelist("test_10_nodi.edgelist")
# print('Il grafo di test (quello letto) ha: ', list(nx.nodes(test_graph)), ' nodi')
# print('Il grafo di test (quello letto) ha: ', test_graph.edges, ' archi')
working_graph = nx.convert_node_labels_to_integers(test_graph)
# print('Il grafo di lavoro ha: ', list(nx.nodes(working_graph)), ' nodi')
# print('Il grafo di lavoro ha: ', working_graph.edges, ' archi')
for i in range(3):
    print("lavoro...")
    sleep(1)
mapped_vertex = dict(couple for couple in zip(nx.nodes(working_graph), nx.nodes(test_graph)))
spectral_partition(working_graph, 60, 40)
nx.relabel_nodes(working_graph, mapped_vertex, copy=False)
# print('Il grafo di lavoro, dopo il clustering, ha: ', list(nx.nodes(working_graph)), ' nodi')
# print('Il grafo di lavoro, dopo il clustering, ha: ', working_graph.edges, ' archi')
'''

'''-------------------------------------------------------------------------------------------------------'''

'''options = {
    'node_color': 'black',
    'node_size': 25,
    'line_color': 'grey',
    'linewidths': 0,
    'width': 0.1,
}
nx.draw(test_graph, **options)
plt.show()
print(nx.number_of_nodes(test_graph))
print(nx.number_of_edges(test_graph))'''

'''--------------------------------------------------------------------------------------------------'''

# per controllare eventuali modifiche apportate alla copia di un grafo

test_graph = fast_gnp_random_graph(10, 0.2)
print("test ha archi:\n", test_graph.edges)
print('test ha: ', test_graph.number_of_edges(), ' archi')
working_graph = nx.convert_node_labels_to_integers(test_graph)
working_graph.add_edge(2, 5)
working_graph.add_edge(3, 9)
print("dopo copia e lavoro test ha archi:\n", test_graph.edges)
print('dopo copia e lavoro test ha: ', test_graph.number_of_edges(), ' archi')
print("dopo copia e lavoro working ha archi:\n", working_graph.edges)
print('dopo copia e lavoro working ha: ', working_graph.number_of_edges(), ' archi')

'''--------------------------------------------------------------------------------------------------'''

# per controllare il passaggio di parametri alle funzioni

def test_function(a):
    lung = len(a)
    if lung == 0:
        print(a)

x = (1, 2)
test_function(x)
x = ()
test_function(x)

G = nx.path_graph(4)
nx.add_path(G, [10, 11, 12])
for set in nx.connected_components(G):
    H = nx.graph(G.subgraph(set))
    print("questa componente ha archi:\n", H.edges)