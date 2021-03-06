import networkx as nx
import pickle
import pandas as pd


def get_list(flights_string):
    return flights_string[2:-2].replace("'", "").split()


def to_index(flight, mapped_flights):
    return mapped_flights[flight]


# df deve essere composto solo dalle colonne 'ID' e 'FLIGHTS' rispettivamente in posizione [0] e [1]
def components_in_graph(df, G, mapped_flights):

    for i in range(0, len(df)):

        flights = get_list(df.iat[i, 1])
        component_nodes = [to_index(flight, mapped_flights) for flight in flights]
        # print(component_nodes)

        if df.iat[i, 0] == 'None':
            # trovati i voli isolati
            continue
            # C = nx.Graph()
            # C.add_nodes_from(component_nodes)
        else:
            # componente generica
            C = nx.subgraph(G, component_nodes)

        yield C


def mean_degree(C):
    """Calcola il grado medio dei nodi di un grafo"""
    nodes_degree = [len(set(nx.neighbors(C, n))) for n in C]
    mean_degree = sum(nodes_degree) / nx.number_of_nodes(C)
    return mean_degree


if __name__ == "__main__":

    node_csv_path = "/home/utente/Scaricati/Tesi/index_flight.csv"
    edgelist_path = "/home/utente/Scaricati/Tesi/edgelist_3"
    louvain_path = "/home/utente/Scaricati/Tesi/Louvain_3.csv"
    sp_louvain_path = "/home/utente/Scaricati/Tesi/sp_from_louvain.csv"
    res_directory = "/home/utente/Scaricati/Tesi/"
    F = nx.Graph()

    # Per leggere i nodi di un grafo da un file csv.
    nodes = pd.read_csv(node_csv_path)
    data = nodes.set_index('Index').to_dict('index').items()
    F.add_nodes_from(data)

    # Per leggere l' edgelist.
    with open(edgelist_path, "rb") as fp:
        edgelist = pickle.load(fp)
    F.add_edges_from(edgelist)

    _mapped_flights = dict(zip(nodes['Flight'], nodes['Index']))

    # Leggo i df
    louvain_df = pd.read_csv(louvain_path)
    sp_louvain_df = pd.read_csv(sp_louvain_path)

    # Creo le componenti, esclusa quella dei voli isolati
    louvain_components = list(components_in_graph(louvain_df[['MOD_CLASS', 'FLIGHTS']],
                                                  F,
                                                  _mapped_flights))
    sp_louvain_components = list(components_in_graph(sp_louvain_df[['COMPONENT_ID', 'FLIGHTS']],
                                                     F,
                                                     _mapped_flights))

    # Calcolo dei parametri interessanti

    # Numero di archi interni: mi aspetto che comm. det. ne abbia molti di più
    n_of_edges_louv = [nx.number_of_edges(C) for C in louvain_components]
    n_of_edges_louv.append(None)

    # Densità: legato al parametro precedente me la aspetto più alta su comm. det.
    density_louv = [nx.density(C) for C in louvain_components]
    density_louv.append(None)

    # Grado medio dei nodi: "figlio" del parametro precedente, mi aspetto la stessa cosa del numero di archi
    mean_degree_louv = [mean_degree(C) for C in louvain_components]
    mean_degree_louv.append(None)

    # Numero delle componenti connesse all'interno della componente: per comm. dect. mi aspetto sempre 1 a differenza
    # dello spectral part.
    connected_comp_louv = [nx.number_connected_components(C) for C in louvain_components]
    connected_comp_louv.append(None)

    # Autovalore di Fiedler: quanto è difficile da da dividere quella componente? Me lo aspetto più alto per comm. det.
    # Potrebbe volerci un bel po' di tempo per calcolarlo
    fiedler_eigevalue_louv = [nx.algebraic_connectivity(C, method='lanczos') for C in louvain_components]
    fiedler_eigevalue_louv.append(None)

    # Creo i df che salverò
    # Suppongo che la comp. dei voli isolati sia messa in fondo
    louvain_columns = {'MOD_CLASS': louvain_df['MOD_CLASS'],
                       'DENSITY': density_louv,
                       'MEAN_DEGREE': mean_degree_louv,
                       'CONNECTED_COMP': connected_comp_louv,
                       'FIEDLER_EIGENVALUE': fiedler_eigevalue_louv}

    res_louvain_df = pd.DataFrame(louvain_columns)

    res_louvain_df.to_csv(res_directory + 'louvain_3_info', header=True, index=False)






