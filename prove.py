import networkx as nx
import pickle
import pandas as pd
import sys


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


def get_flights(G):
    """
    Ottiene una lista contente i nomi dei voli all'interno del grafo G.

    Da usare sulle componenti dello spectral_partitioning.

    :param G: grafo avente nodi con l'attributo "Flight"
    :return: lista con il valore dell'attributo "Flight" di ciascun nodo di G
    """
    _flights = [fli for ind, fli in G.nodes(data="Flight")]
    return _flights


def fill_singleton(S, flight_list):
    """
    Riempie la lista dei voli che formano una componente a sé stante.

    :param S: grafo composto da un solo nodo
    :param flight_list: lista contentente i nomi dei voli isolati
    :return: None
    """
    flight = get_flights(S)
    flight_list.extend(flight)


def fill_df_with_component(_flights, _size, sp_df):
    """
    Riempie sp_df con i voli e il loro numero.

    :param _flights: lista contenete i voli
    :param _size: numero di voli della componente
    :param sp_df: datafrae da riempire
    :return: sp_df con l'aggiunta della riga relativa alla componente
    """
    row = pd.DataFrame({"FLIGHTS": [_flights], "SIZE": _size})
    return sp_df.append(row, ignore_index=True)


def fill_df_with_singleton(_flights, _size, sp_df):
    """
    Riempie sp_df con la riga relativa ai nodi isolati.

    :param _flights: lista contenete i voli isolati
    :param _size: numero di voli isolati
    :param sp_df: dataframe da riempire
    :return: sp_df con l'aggiunta della riga relativa ai voli isolati
    """
    row = pd.DataFrame({"ID": "None", "FLIGHTS": [_flights], "SIZE": _size})
    return sp_df.append(row)


def fill_nodes_with_singleton(amount, nodes):
    """
    Riempie nodes con una componente composta da un singolo nodo.

    :param amount: numero di singleton
    :param nodes: lista con il numero dei vertici per ogni componente
    :return: None
    """
    for n in range(amount):
        nodes.append(1)


def fill_nodes_with_component(_size, nodes):
    """
    Riempie nodes con la taglia della componente.

    :param _size: dimensione della componente
    :param nodes: lista con il numero dei vertici per ogni componente
    :return: None
    """
    nodes.append(_size)


def get_nodes_from(df):
    """
    A partire dai df di louvain o infomap fornisce una lista con il numero di nodi di ciascuna componente.

    :param df: infomap_df o louvain_df
    :return: Lista con il numero di nodi in ciascuna componente
    """
    nodes = []

    n_of_rows = len(df.index)

    for i in range(n_of_rows):
        if df.index[i] == "None":
            # Trovata la componente dei voli isolati
            fill_nodes_with_singleton(df["SIZE"].iloc[i], nodes)
        else:
            # Trovata una componente generica
            fill_nodes_with_component(df["SIZE"].iloc[i], nodes)

    return nodes


def get_flights_graph(nodes_path, edges_path):
    """
    Legge il grafo di partenza a partire dai percorsi contenenti i nodi e gli archi.

    :param nodes_path: percorso del file csv contenente i nodi
    :param edges_path: percorso del file pickle contenente gli archi
    :return: grafo G
    """
    G = nx.Graph()
    # Per leggere tutti i nodi del grafo di partenza.
    nodes_df = pd.read_csv(nodes_path, index_col="Index")
    data = nodes_df.to_dict('index').items()
    G.add_nodes_from(data)
    # Per leggere gli archi del grafo di partenza
    with open(edges_path, "rb") as fp:
        edgelist = pickle.load(fp)
    G.add_edges_from(edgelist)  # Gli archi si basano sulla mappatura in interi dei voli
    return G


if __name__ == "__main__":

    # Percorsi dei file e delle directory usate.
    node_csv_path = "/home/utente/Scaricati/Tesi/index_flight.csv"
    edgelist_path = "/home/utente/Scaricati/Tesi/edgelist_3"
    louvain_path = "/home/utente/Scaricati/Tesi/Louvain_3.csv"
    infomap_path = "/home/utente/Scaricati/Tesi/Infomap_3.csv"
    write_directory = "/home/utente/Scaricati/Tesi/"

    # Da quale file leggere il numero di nodi delle componenti
    compare = "infomap"

    # Prepara il grafo F, inserendo nodi e archi
    F = get_flights_graph(node_csv_path, edgelist_path)

    print("I nodi sono: ", nx.number_of_nodes(F))
    print("Attributi dei nodi sono del tipo: ", F.nodes[0])
    print("Gli archi sono: ", nx.number_of_edges(F))

    if compare == "louvain":
        result_filename = "spectral_partitioning_from_louvain.csv"
        louvain_df = pd.read_csv(louvain_path, index_col="MOD_CLASS")
        components = get_nodes_from(louvain_df)
        print("Prima parte dei nodi: ", components[:3])
        print("Parte finale dei nodi: ", components[:-10:-1])
        print("Tutti i nodi: ", components)
    elif compare == "infomap":
        result_filename = "spectral_partitioning_from_infomap.csv"
        infomap_df = pd.read_csv(infomap_path, index_col="CLUSTER")
        components = get_nodes_from(infomap_df)
        print("Prima parte dei nodi: ", components[:3])
        print("Parte finale dei nodi: ", components[:-10:-1])
    else:
        result_filename = "spectral_partitioning.csv"
        components = [14958, 14959]

    # F = nx.fast_gnp_random_graph(100, .5)
    # nodes = [10, 80, 1, 1, 1, 1, 1, 5]

    # Df usato per salvare i risultati dell'algoritmo
    spectral_df = pd.DataFrame(columns=["ID", "FLIGHTS", "SIZE"])

    # Lista in cui salvo i nomi dei voli isolati
    singleton_flights = []  # Lista contenente i nomi dei voli isolati eventualmente presenti

    # Esecuzione dell'algoritmo e salvataggio all'ineterno di spectral_df
    for C in spectral_partitioning(F, components):
        size = C.number_of_nodes()
        if size == 1:
            # Ho trovato un nodo isolato
            fill_singleton(C, singleton_flights)
        else:
            # Ho trovato una componente generica
            flights = get_flights(C)
            spectral_df = fill_df_with_component(flights, size, spectral_df)

    # Ordino per dimensione delle componenti
    spectral_df.sort_values(by=["SIZE"], inplace=True, ascending=False)

    # ID delle componenti che segue la loro dimensione
    spectral_df.reset_index(drop=True, inplace=True)
    spectral_df["ID"] = spectral_df.index

    # Se alla fine ho dei nodi isolati li aggiungo
    if singleton_flights:
        n_of_isolated_nodes = len(singleton_flights)
        spectral_df = fill_df_with_singleton(singleton_flights, n_of_isolated_nodes, spectral_df)

    # Salvataggio csv
    spectral_df.to_csv(write_directory + result_filename, index=False)
