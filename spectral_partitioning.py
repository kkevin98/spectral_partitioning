import networkx as nx
import pickle


def _basic_partitioning(G, n1, n2):
    """
    Genera le 2 classi composte da n1 e n2 nodi a partire da G.
    La divisione viene effettuata con l'algoritmo spettrale
    Da usare all'interno di spectral_partitioning(G, class_nodes)
    :param G: grafo semplice connesso
    :param n1: nodi della prima classe
    :param n2: nodi della seconda classe
    :return: un sottografo, vista di G. La struttura del sottografo non può essere modificata
    """

    # Lista si nodi ordinati secondo il vettore di Fiedler
    ordered_nodes = nx.spectral_ordering(G) # Torna una list non un nunmpy array

    component_test1 = set(ordered_nodes[:n1])
    component_test2 = set(ordered_nodes[:n2])

    cut_size_1 = nx.cut_size(G, component_test1)
    cut_size_2 = nx.cut_size(G, component_test2)

    # Scelgo la componente che dividerà il grafo in base al peso del suo insieme di taglio
    if cut_size_1 < cut_size_2:
        component_final = component_test1
        remaining_nodes = set(ordered_nodes[n1:])
    else:
        component_final = component_test2
        remaining_nodes = set(ordered_nodes[n2:])

    G_1 = G.subgraph(component_final)
    G_2 = G.subgraph(remaining_nodes)
    yield from (G_1, G_2)


def spectral_partitioning(G, class_nodes):
    """
    Genera un numero di classi composte da un certo numero di nodi a partire da G
    :param G: grafo semplice connesso
    :param class_nodes: lista o tupla contenente il numero di vertici di ciascuna componente
    :return: generatore di grafi
    """

    G_nodes = nx.number_of_nodes(G)
    given_nodes = sum(class_nodes)

    if given_nodes != G_nodes:
        raise nx.NetworkXException("Invalid classes")
    if nx.is_weighted(G):
        raise nx.NetworkXNotImplemented("Weighted graph.")
    if nx.is_directed(G):
        raise nx.NetworkXNotImplemented("Directed graph.")
    if nx.number_of_selfloops(G):
        raise nx.NetworkXNotImplemented("Graph with self-edges.")

    classes = len(class_nodes) # numero delle componenti in cui dividere G

    if classes == 1:
        yield G
    else:
        half = classes // 2
        big_class1_nodes = sum(class_nodes[:half])
        big_class2_nodes = sum(class_nodes[half:])
        # divido in 2 G e delego il compito di proseguire con la divisione
        for component in _basic_partitioning(G, big_class1_nodes, big_class2_nodes):
            component_nodes = nx.number_of_nodes(component)
            if component_nodes == big_class1_nodes:
                yield from spectral_partitioning(component, class_nodes[:half])
            else:
                yield from spectral_partitioning(component, class_nodes[half:])



if __name__ == "__main__":

    # Per leggere un edgelist.
    with open("/home/utente/Scaricati/Tesi/edgelist_3", "rb") as fp:
        edgelist = pickle.load(fp)

    F = nx.Graph()
    F.add_edges_from(edgelist)

    print("I nodi sono: ", nx.number_of_nodes(F))
    print("Gli archi sono: ", nx.number_of_edges(F))

    # Numero di nodi in ciascuna classe.
    nodes = [12191, 12191]

    # Calcolo e salvataggio delle classi. Un file per ognuna di esse.
    for i, component in enumerate(spectral_partitioning(F, nodes)):
        nx.write_gpickle(component, "/home/utente/Scaricati/Tesi/edgelist_component_{}".format(i + 1))