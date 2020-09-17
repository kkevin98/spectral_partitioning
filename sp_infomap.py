import networkx as nx
import pickle
import pandas as pd
import spectral_partitioning as sp
import numpy as np
import sys

np.set_printoptions(threshold=sys.maxsize)


def clear_cluster(column):
    """
    Trasforma il dtype dei valori all'interno della colonna (object-->Int64).

    :param column: "MOD_CLASS" con valori object
    :return: colonna "MOD_CLASS" con valori Int64
    """
    return pd.to_numeric(column, errors="coerce").astype("Int64")


def get_components_size(df):
    """
    A partire dal datframe di Louvain, ottenuto dal relativo cvs, indica il numero di nodi
    all'interno di ciascuna componente.

    :param df: dataframe di Louvain con la colonna "MOD_CLASS" "ripulita" (vedi: clear_mod_class)
    :return: lista con all'interno il numero di nodi (sottoforma di pd.Int64) in ciascuna componente
    """
    components_size = []
    for row in range(len(df)):
        if pd.isna(df.at[row, "CLUSTER"]):
            # Ho trovato la componente dei voli isolati
            for t in range(df.at[row, "SIZE"]):
                components_size.append(1)
        else:
            components_size.append(df.at[row, "SIZE"])
    return components_size


def get_component_id(component_size, id_size_dict):
    """
    Risale all'Id della componente a partire dal suo numero di nodi.

    :param component_size: numero di nodi all'interno della componente
    :param id_size_dict: dizionario dove la key contiene l'id della componente e il value la sua dimensione
    :return: id della componente
    """
    if component_size == 1:  # È un volo isolato --> Id = "None"
        return "None"
    else:
        for comp_id, size in id_size_dict.items():
            if size == component_size:
                del id_size_dict[comp_id]
                return comp_id


def fill_mapped_flights(G, comp_id):
    """
    Riempie mapped_flights con il nome del volo associandogli l'Id della componente a cui appartiene.

    :param G: componente ottenuta da spectral_partitioning
    :param comp_id: Id della componente G
    :return: None
    """
    for ind, fli in G.nodes(data="Flight"):
        mapped_flights[fli] = comp_id


if __name__ == "__main__":

    node_csv_path = "/home/utente/Scaricati/Tesi/index_flight.csv"
    edgelist_path = "/home/utente/Scaricati/Tesi/edgelist_3"
    infomap_path = "/home/utente/Scaricati/Tesi/Infomap_3.csv"
    spectral_path = "/home/utente/Scaricati/Tesi/sp_from_infomap.csv"
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
    print("Attributi dei nodi sono del tipo: ", list(F.nodes(data="Flight"))[0])
    print("Gli archi sono: ", nx.number_of_edges(F))

    # Leggo il file di louvain
    infomap_df = pd.read_csv(infomap_path)

    # Preparo "MOD_CLASS" per essere usata
    infomap_df["CLUSTER"] = clear_cluster(infomap_df["CLUSTER"])

    # Associo ad ogni componente la sua taglia
    id_to_size = dict(zip(infomap_df["CLUSTER"], infomap_df["SIZE"]))

    # Trovo le componenti in cui dividerò F
    nodes_in_components = get_components_size(infomap_df)

    # F = F.subgraph(range(100))
    # nodes_in_components = [1, 1, 1, 1, 1, 20, 20, 5, 50]
    # id_to_size = {0: 20, 1: 50, 2: 20, 3: 5, None: 5}

    # Dizionario in cui inserisco nome_volo-->id
    mapped_flights = {}

    # Calcolo e salvataggio delle classi. Un file per ognuna di esse.
    for C in sp.spectral_partitioning(F, nodes_in_components):
        _size = C.number_of_nodes()
        component_id = get_component_id(_size, id_to_size)
        fill_mapped_flights(C, component_id)

    flight_to_id_df = pd.DataFrame(mapped_flights.items(), columns=["flight", "component"]).sort_values(by=["flight"])

    # Non mi occupo della size del cluster perchè la posso ottenere facilmente dal csv di Louvain
    spectral_df = flight_to_id_df.groupby(["component"])["flight"].unique()

    spectral_df = pd.DataFrame({"GROUP_ID": spectral_df.index,
                                "FLIGHTS": spectral_df.values})

    spectral_df["SIZE"] = 0
    for i in range(0, len(spectral_df)):
        spectral_df.at[i, "SIZE"] = len(spectral_df.at[i, "FLIGHTS"])

    spectral_df.to_csv(spectral_path, header=True, index=False)
