import networkx as nx
import numpy as np
from networkx.linalg.algebraicconnectivity import algebraic_connectivity, fiedler_vector
from networkx.algorithms.cuts import cut_size
import matplotlib.pyplot as plt
from networkx.classes.function import (
    nodes_with_selfloops,
    is_empty,
    is_directed,
    is_weighted,
    number_of_selfloops,
    neighbors,
    nodes,
    number_of_nodes
)


def remove_self_edges(G):
    '''Return G without self-edges'''
    G.remove_edges_from((n, n) for n in nodes_with_selfloops(G))


def graph_division(G, component):
    '''Remove the edges in the cut-set of components.
    To use into spectral_partition.
    Works with simple graph.
    '''
    result_G = G.copy()
    for n1 in component:
        for n2 in result_G.nodes:
            if n2 not in component and result_G.has_edge(n1, n2):
                result_G.remove_edge(n1, n2)
    return result_G



def get_mapped_vector(v):
    ''''''
    # works only with numerical vectors
    num_rows = np.shape(v)[0]
    index_array = np.arange(num_rows, dtype=np.float64)
    res = np.zeros((num_rows, 2))
    res[:, 0] = index_array
    res[:, 1] = v
    # print("get mappe ritorna: ", res.dtype.name)
    # print(res)
    return res


def get_sorted_vector(v):
    ''''''
    return np.sort(v.view('f8, f8'), order=['f1'], axis=0).view(np.float64)


def _basic_partitioning(G, n1, n2):
    '''Return graph G divided in two parts of specified sizes'''

    '''n = len(G)

    if number_of_selfloops(G):
        raise nx.NetworkXNotImplemented("Graph with self-edges.")
    if is_weighted(G):
        raise nx.NetworkXNotImplemented("Weighted graph.")
    if is_directed(G):
        raise nx.NetworkXNotImplemented("Directed graph.")
    if is_empty(G):
        raise nx.NetworkXNotImplemented("Empty graph.")
    if not nx.is_connected(G):
        raise nx.NetworkXException("Non connected graph.")
    if n < 2:
        raise nx.NetworkXException("Too small graph.")
    if n1 + n2 != n:
        raise nx.NetworkXException("Invalid components.")'''

    # Preparo il vettore da cui estrarrò le componenti
    v2 = fiedler_vector(G)
    # print("v2: ", v2.shape, v2.dtype.name)
    # print("il fiedler vector è:\n", v2)
    # print("Somma degli elementi dell'autovettore di fiedler: ", v2.sum()) # Dovrebbe essere circa 0
    mapped_v2 = get_mapped_vector(v2)
    # print("mapped_v2: ", mapped_v2.shape, mapped_v2.dtype.name)
    # print("l'arrey mappato è:\n", mapped_v2)
    sorted_v2 = get_sorted_vector(mapped_v2)
    # print("l'arrey ordinato è:\n", sorted_v2)

    # Creo e controllo le due classi e relativi insiemi di taglio
    component_test1 = set(sorted_v2[:n1, 0].flat)
    component_test2 = set(sorted_v2[:n2, 0].flat)
    print("Questo è component_test1:\n", component_test1)
    print("Questo è component_test2:\n", component_test2)
    cut_size_1 = cut_size(G, component_test1)
    cut_size_2 = cut_size(G, component_test2)
    print("Il primo cut size vale: ", cut_size_1)
    print("Il secondo cut size vale: ", cut_size_2)


    # Rimuovo gli archi del grafo che fanno parte dell'insieme di taglio
    if cut_size_1 < cut_size_2:
        component_final = component_test1
        H = graph_division(G, component_final)
        return H
    else:
        component_final = component_test2
        H = graph_division(G, component_final)
        return H



'''def spectral_spectral_partition(G, n1, n2, classes=2):
    'x''Spectral partitioning with number of classes'x''

    n = len(G)

    if is_empty(G):
        raise nx.NetworkXNotImplemented("Empty graph.")
    if n/classes < 1:
        raise nx.NetworkXException("Too many classes.")
    if n < 2:
        raise nx.NetworkXException("Too small graph.")
    if (n1 is not None and
        n2 is None):
        raise nx.NetworkXException("Invalid components.")
    if (n1 is None and
        n2 is not None):
        raise nx.NetworkXException("Invalid components.")
    if n1 + n2 != n:
        raise nx.NetworkXException("Invalid components.")
    if is_weighted(G):
        raise nx.NetworkXNotImplemented("Weighted graph.")
    if is_directed(G):
        raise nx.NetworkXNotImplemented("Directed graph.")
    if number_of_selfloops(G):
        raise nx.NetworkXNotImplemented("Graph with self-edges.")
    if not nx.is_connected(G):
        raise nx.NetworkXException("Non connected graph.")'''


def _working_components(G):
    '''
    G è un grafo indiretto
    Fornisce un generatore delle componenti di G
    '''
    for set in nx.connected_components(G):
        yield G.subgraph(set).copy()


def spectral_partitioning(G, class_nodes):
    # per integrore la parte di gestione dei nodi da stringhe a interi crea un'altra funzione
    # classes dev'essere una lista o una tupla

    G_nodes = number_of_nodes(G)
    given_nodes = sum(class_nodes)

    if is_empty(G):
        raise nx.NetworkXNotImplemented("Empty graph.")
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
    if not nx.is_connected(G):
        raise nx.NetworkXException("Not connected graph.")
    # valuta il caso in cui classes == None e classes vuoto/a
    # suppongo che class_nodes sia una lista

    classes = len(class_nodes)

    if classes == 1:
        yield G
    else:
        half = classes // 2
        big_class1_nodes = sum(class_nodes[:half])
        big_class2_nodes = sum(class_nodes[half:])
        # working_graph = nx.convert_node_labels_to_integers(test_graph)
        temp_G = _basic_partitioning(G, big_class1_nodes, big_class2_nodes)
        nx.draw(temp_G, with_labels=True)
        plt.savefig("debug.png")
        plt.clf()
        # meglio component_generator
        for component in _working_components(temp_G):
            component_nodes = number_of_nodes(component)
            if component_nodes == big_class1_nodes:
                yield from spectral_partitioning(component, class_nodes[:half])
            else:
                yield from spectral_partitioning(component, class_nodes[half:])