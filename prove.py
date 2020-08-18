import networkx as nx
import numpy as np
import sys
from time import sleep
import matplotlib.pyplot as plt
from networkx.generators.random_graphs import fast_gnp_random_graph
from networkx.linalg.algebraicconnectivity import algebraic_connectivity, fiedler_vector, spectral_ordering
from networkx.algorithms.components import connected_components
# from my_network_lib import spectral_partition
from networkx.algorithms.cuts import cut_size
from networkx.drawing.nx_agraph import (
    to_agraph,
    write_dot,
)
import pygraphviz as pgv
from networkx.classes.function import (
    to_directed,
    nodes,
    nodes_with_selfloops,
    is_empty,
    is_directed,
    is_weighted,
    number_of_selfloops,
    number_of_nodes,
    number_of_edges
)
from my_network_lib import remove_self_edges, spectral_partitioning, _basic_partitioning, _working_components


def second_basic_partitioning(G, n1, n2):
    """
    Genera le 2 classi composte da n1 e n2 nodi a partire da G.
    La divisione viene effettuata con l'algoritmo spettrale
    Da usare all'interno di spectral_partitioning(G, class_nodes)
    :param G: grafo semplice connesso
    :param n1: nodi della prima classe
    :param n2: nodi della seconda classe
    :return: un sottografo, vista di G. La struttura del sottografo non può essere modificata
    """

    ordered_nodes = spectral_ordering(G) # Torna una list non un nunmpy array
    # print("I nodi ordinati sono:\n", ordered_nodes)

    component_test1 = set(ordered_nodes[:n1])
    component_test2 = set(ordered_nodes[:n2])
    # print("Questo è component_test1:\n", component_test1)
    # print("Questo è component_test2:\n", component_test2)

    cut_size_1 = cut_size(G, component_test1)
    cut_size_2 = cut_size(G, component_test2)
    # print("Il primo cut size vale: ", cut_size_1)
    # print("Il secondo cut size vale: ", cut_size_2)

    if cut_size_1 < cut_size_2:
        component_final = component_test1
        remaining_nodes = set(ordered_nodes[n1:])
    else:
        component_final = component_test2
        remaining_nodes = set(ordered_nodes[n2:])

    # print("Le 2 divisioni finali sono:\n", component_final, "\n", remaining_nodes)

    G_1 = G.subgraph(component_final)
    G_2 = G.subgraph(remaining_nodes)
    yield from (G_1, G_2)


def second_spectral_partitioning(G, class_nodes):
    """
    Genera un numero di classi composte da un certo numero di nodi a partire da G
    :param G: grafo semplice connesso
    :param class_nodes: lista o tupla contenente il numero di vertici di ciascuna componente
    :return: generatore di grafi
    """

    G_nodes = number_of_nodes(G)
    given_nodes = sum(class_nodes)


    # is_empty(G) è severo, non mi lascia passare eventuali singleton
    # ES: spectral_partitioning(G, [1, 1]), G con 2 nodi e un arco
    #if is_empty(G):
    #    raise nx.NetworkXNotImplemented("Empty graph.")


    # Vedi is_empty(G)
    # if G_nodes < 2:
    #    raise nx.NetworkXException("Too small graph.")


    if given_nodes != G_nodes:
        raise nx.NetworkXException("Invalid classes")
    if is_weighted(G):
        raise nx.NetworkXNotImplemented("Weighted graph.")
    if is_directed(G):
        raise nx.NetworkXNotImplemented("Directed graph.")
    if number_of_selfloops(G):
        raise nx.NetworkXNotImplemented("Graph with self-edges.")


    # Però blocco eventuali grafi non connessi
    # ES: spectral_partitioning(G, [1, 1]), G con 2 nodi, ma senza archi
    # if not nx.is_connected(G):
    #     raise nx.NetworkXException("Not connected graph.")


    classes = len(class_nodes) # numero delle componenti in cui dividere G

    if classes == 1:
        yield G
    else:
        half = classes // 2
        big_class1_nodes = sum(class_nodes[:half])
        big_class2_nodes = sum(class_nodes[half:])
        # divido in 2 G e delego il compito di proseguire con la divisione
        for component in second_basic_partitioning(G, big_class1_nodes, big_class2_nodes):
            component_nodes = number_of_nodes(component)
            if component_nodes == big_class1_nodes:
                yield from second_spectral_partitioning(component, class_nodes[:half])
            else:
                yield from second_spectral_partitioning(component, class_nodes[half:])

if __name__ == "__main__":

    test_graph = fast_gnp_random_graph(100, .05)
    # test_graph = nx.read_edgelist("test_10_nodi.edgelist")
    print("Questo è il grafo di partenza")
    # print(test_graph.nodes)
    print("I nodi sono: ", number_of_nodes(test_graph))
    # print(test_graph.edges)
    print("Gli archi sono: ", number_of_edges(test_graph))

    '''
    for component in second_basic_partitioning(test_graph, 60, 40):
        print("[Basic partitioning]:\n", component.nodes, "\n", component.edges)
    
    print("Test che non ho modificato il grafo originale:\n", test_graph.edges)
    '''

    print("--------------------------------------------------------------------------------------------------------------")

    """
    # sys.exit()

    # Per disegnare i grafi
    nx.draw(test_graph, with_labels=True)
    plt.savefig("debug.png")
    plt.clf()
    """

    nodes = [25, 25, 25, 25]
    for component in second_spectral_partitioning(test_graph, nodes):
        print("fatto!!")
        print("I nodi sono: ", number_of_nodes(component))
        print("Gli archi sono: ", number_of_edges(component))
        # print("[Spectral_partitioning]:\n", component.nodes, "\n", component.edges)