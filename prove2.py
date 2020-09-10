import networkx as nx
import pickle
import pandas as pd


def get_list(flights_string):
    return flights_string[1:-1].split()


def flights_in_common(row):
    louvain_flights_list = get_list(row["LOUVAIN_FLIGHTS"])
    sp_flights_list = get_list(row["SP_FLIGHTS"].replace(",", " "))
    n_in_common = len(set(louvain_flights_list) & set(sp_flights_list))
    return n_in_common

def edges_per_component(row):



if __name__ == "__main__":

    node_csv_path = "/home/utente/Scaricati/Tesi/index_flight.csv"
    edgelist_path = "/home/utente/Scaricati/Tesi/edgelist_3"
    louvain_path = "/home/utente/Scaricati/Tesi/Louvain_3.csv"
    infomap_path = "/home/utente/Scaricati/Tesi/Infomap_3.csv"
    sp_louvain_path = "/home/utente/Scaricati/Tesi/sp_from_louvain.csv"
    sp_infomap_path = "/home/utente/Scaricati/Tesi/sp_from_infomap.csv"
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

    # Louvain
    louvain_df = pd.read_csv(louvain_path)
    louvain_df = louvain_df.rename(columns={"MOD_CLASS": "ID", "FLIGHTS": "LOUVAIN_FLIGHTS"})

    sp_louvain_df = pd.read_csv(sp_louvain_path)
    sp_louvain_df = sp_louvain_df.rename(columns={"FLIGHTS": "SP_FLIGHTS"})

    compare_louvain_df = pd.merge(louvain_df, sp_louvain_df, on=["ID", "SIZE"])

    compare_louvain_df["IN_COMMON"] = compare_louvain_df.apply(flights_in_common, axis=1)

    # Ricostruisco un grafo
    


    # Infomap