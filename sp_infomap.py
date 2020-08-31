import networkx as nx
import pickle
import pandas as pd


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

    classes = len(class_nodes)  # numero delle componenti in cui dividere G

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


def get_nodes(id_size_dict):
    res = []
    n_of_isolated_flights = id_size_dict.pop("None", 0)
    for n in range(n_of_isolated_flights):
        res.append(1)
    res.extend(id_size_dict.values())
    return res


def get_flights(G):
    """
    Ottiene una lista contente i nomi dei voli all'interno del grafo G.

    Da usare sulle componenti dello spectral_partitioning.

    :param G: grafo avente nodi con l'attributo "Flight"
    :return: lista con il valore dell'attributo "Flight" di ciascun nodo di G
    """
    flights = [fli for ind, fli in G.nodes(data="Flight")]
    return flights


def get_id(id_size_dict, wanted_size):
    for comp_id, size in id_size_dict.items():
        if size == wanted_size:
            del id_size_dict[comp_id]
            return comp_id


def get_spectral_df(G, class_nodes, comp_to_size):

    isolated_flights = []
    flights_column = []
    id_column = []
    size_column = []

    # Calcolo e salvataggio delle classi. Un file per ognuna di esse.
    for C in spectral_partitioning(G, class_nodes):
        size = C.number_of_nodes()
        if size == 1:
            flight = get_flights(C)
            isolated_flights.extend(flight)
        else:
            flights = get_flights(C)
            flights.sort()
            comp_id = get_id(comp_to_size, size)
            # Ottenuto quello di cui avevo bisogno, aggiorno le liste delle colonne
            id_column.append(comp_id)
            flights_column.append(flights)
            size_column.append(size)

    # Mi occupo dei voli isolati, se presenti
    if isolated_flights:
        amount = len(isolated_flights)
        isolated_flights.sort()
        id_column.append("None")
        flights_column.append(isolated_flights)
        size_column.append(amount)

    df = pd.DataFrame({"ID": id_column,
                       "FLIGHTS": flights_column,
                       "SIZE": size_column}).sort_values(by="ID")

    return df


if __name__ == "__main__":

    node_csv_path = "/home/utente/Scaricati/Tesi/index_flight.csv"
    edgelist_path = "/home/utente/Scaricati/Tesi/edgelist_3"
    infomap_path = "/home/utente/Scaricati/Tesi/Infomap_3.csv"
    spectral_path = "/home/utente/Scaricati/Tesi/spectral_partitioning_from_infomap.csv"
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
    print("Attributi dei nodi sono del tipo: ", F.nodes[0])
    print("Gli archi sono: ", nx.number_of_edges(F))

    # Leggo il file di louvain
    louvain_df = pd.read_csv(infomap_path, index_col="MOD_CLASS")
    id_to_size = dict(zip(louvain_df.index, louvain_df["SIZE"]))
    nodes_in_components = get_nodes(id_to_size)

    # F = F.subgraph(range(100))
    # nodes_in_components = [1, 1, 1, 1, 1, 20, 20, 5, 50]
    # id_to_size = {"0": 20, "1": 50, "2": 20, "3": 5, "None": 5}

    spectral_df = get_spectral_df(F, nodes_in_components, id_to_size)

    spectral_df.to_csv(spectral_path, index=False)
