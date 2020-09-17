import networkx as nx
import pickle
import pandas as pd
import matplotlib.pyplot as plt


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

    # Lista di nodi ordinati secondo il vettore di Fiedler
    ordered_nodes = nx.spectral_ordering(G, method="lanczos")  # Torna una list non un nunmpy array

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


def spectral_partitioning(G, classes_nodes):
    """
    Genera un numero di classi composte da un certo numero di nodi a partire da G.

    :param G: grafo semplice connesso
    :param classes_nodes: lista o tupla contenente il numero di vertici di ciascuna componente
    :return: generatore di grafi
    """

    G_nodes = nx.number_of_nodes(G)
    given_nodes = sum(classes_nodes)

    if (given_nodes != G_nodes) or (0 in classes_nodes):
        raise nx.NetworkXException("Invalid classes")
    if nx.is_weighted(G):
        raise nx.NetworkXNotImplemented("Weighted graph.")
    if nx.is_directed(G):
        raise nx.NetworkXNotImplemented("Directed graph.")
    if nx.number_of_selfloops(G):
        raise nx.NetworkXNotImplemented("Graph with self-edges.")

    classes = len(classes_nodes)  # numero delle componenti in cui dividere G

    if classes == 1:
        yield G
    else:
        half = classes // 2
        big_class1_nodes = sum(classes_nodes[:half])
        big_class2_nodes = sum(classes_nodes[half:])
        # divido in 2 G e delego il compito di proseguire con la divisione
        for component in _basic_partitioning(G, big_class1_nodes, big_class2_nodes):
            component_nodes = nx.number_of_nodes(component)
            if component_nodes == big_class1_nodes:
                yield from spectral_partitioning(component, classes_nodes[:half])
            else:
                yield from spectral_partitioning(component, classes_nodes[half:])


def fill_mapped_nodes(G, comp_id):
    """
    Riempie mapped_nodes con il nodo associandogli l'Id della componente a cui appartiene.

    :param G: componente ottenuta da spectral_partitioning
    :param comp_id: Id della componente G
    :return: None
    """

    size = C.number_of_nodes()
    if size == 1:
        comp_id = "None"

    for n in G:
        mapped_nodes[n] = comp_id


if __name__ == "__main__":

    node_csv_path = "/home/utente/Scaricati/Tesi/index_flight.csv"
    edgelist_path = "/home/utente/Scaricati/Tesi/edgelist_3"
    result_path = "/home/utente/Scaricati/Tesi/sp_test.csv"
    F = nx.Graph()

    # Per leggere i nodi di un grafo da un file csv.
    nodes = pd.read_csv(node_csv_path)
    data = nodes.set_index('Index').to_dict('index').items()
    F.add_nodes_from(data)

    # Per leggere una edgelist.
    with open(edgelist_path, "rb") as fp:
        edgelist = pickle.load(fp)
    F.add_edges_from(edgelist)

    print("I nodi sono: ", nx.number_of_nodes(F))
    print("Struttura del nodo: ", list(F.nodes(data="Flight"))[0])
    print("Gli archi sono: ", nx.number_of_edges(F))

    # Numero di nodi in ciascuna classe.
    nodes = [14958, 14959]

    # Creazione di un grafo casuale
    F = nx.fast_gnp_random_graph(12, .5)
    nodes = [3, 2, 7]

    # Grafo che genera componenti sconnesse
    F = nx.Graph()
    archi = [(0, 2),
             (2, 3),
             (3, 4),
             (2, 4),
             (2, 7),
             (1, 5),
             (5, 6),
             (6, 7),
             (5, 7),
             (5, 4)
             ]
    F.add_edges_from(archi)
    nodes = [2, 6]

    mapped_nodes = {}

    for i, C in enumerate(spectral_partitioning(F, nodes)):
        fill_mapped_nodes(C, i)
        # res_graph = nx.compose(res_graph, C)
        # nx.write_gpickle(component, write_directory+"res_component_{}.pickle".format(i + 1))

    node_to_id_df = pd.DataFrame(mapped_nodes.items(), columns=["node", "group_id"])

    components_df = node_to_id_df.groupby(["group_id"])["node"].unique()
    components_df = pd.DataFrame({"GROUP_ID": components_df.index,
                                  "NODE": components_df.values})

    # Manca la size

    components_df.to_csv(result_path, header=True, index=False, na_rep="None")

    # Salvo le 2 figure: una con i nodi colorati in base alla componente e l'altra normale
    # OSS: I nodi isolati vengono colorati con lo stesso colore poiché
    #      appartengono tutti alla componente "None"
    printing_df = node_to_id_df.set_index('node')
    printing_df = printing_df.reindex(F.nodes())
    # converto in category la colonna "component_id"
    printing_df['group_id'] = pd.Categorical(printing_df['group_id'])

    my_pos = nx.spring_layout(F)
    nx.draw(F,
            with_labels=True,
            pos=my_pos,
            node_size=500,
            font_color="white"
            )
    plt.savefig("mygraph.png")
    plt.clf()

    nx.draw(F,
            with_labels=True,
            pos=my_pos,
            node_color=printing_df['group_id'].cat.codes,  # per ottenere degli interi
            cmap=plt.cm.Set1,
            node_size=500,
            font_color="white"
            )
    plt.savefig("mygraph_res.png")
    plt.clf()

    print(printing_df['group_id'].cat.codes)


    # # Grafo che genera componenti sconnesse
    # F = nx.Graph()
    # archi = [(0, 2),
    #          (2, 3),
    #          (3, 4),
    #          (2, 4),
    #          (2, 7),
    #          (1, 5),
    #          (5, 6),
    #          (6, 7),
    #          (5, 7),
    #          (5, 4)
    #          ]
    # F.add_edges_from(archi)
    # nodes = [2, 6]


    # # Grafo fregatura
    # F = nx.Graph()
    # archi = [(0, 1),
    #          (1, 2),
    #          (2, 3),
    #          (3, 4),
    #          (4, 5),
    #          (6, 7),
    #          (7, 8),
    #          (8, 9),
    #          (9, 10),
    #          (10, 11),
    #          (3, 9),
    #          (4, 10),
    #          (5, 11)
    #          ]
    # F.add_edges_from(archi)
    # nodes = [6, 6]