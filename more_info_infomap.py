import networkx as nx
import pickle
import pandas as pd


def get_list(flights_string):
    """
    Ottiene i voli di una componente sottoforma di lista
    :param flights_string: contenuto della cella con i voli della componente
    :return: lista dei voli della componente
    """
    return flights_string[2:-2].replace("'", "").split()


def to_index(flight, mapped_flights):
    """
    Associa al nome del volo il suo corrispondente sottoforma di intero
    :param flight: stringa del nome del volo
    :param mapped_flights: dizionario con nome del volo come key e "id" del volo
    :return: "id" del volo
    """
    return mapped_flights[flight]


# df deve essere composto solo dalle colonne 'ID' e 'FLIGHTS' rispettivamente in posizione [0] e [1]
def components_in_graph(df, G, mapped_flights):
    """
    A partire dai df di louvain e sp_louvain fornisce una ad una le componenti.

    :param df: louvain_df, sp_louvain_df, infomap_df, sp_infomap_df
    :param G: Grafo dei voli europei
    :param mapped_flights: dizionario con nome del volo come key e "id" del volo
    :return: #
    """

    for i in range(0, len(df)):

        flights = get_list(df.iat[i, 1])
        component_nodes = [to_index(flight, mapped_flights) for flight in flights]
        # print(component_nodes)

        if df.iat[i, 0] == 'None':
            # trovati i voli isolati
            # continue
            C = nx.Graph()
            C.add_nodes_from(component_nodes)
        else:
            # componente generica
            C = nx.subgraph(G, component_nodes)

        yield C


def mean_degree(C):
    """Calcola il grado medio dei nodi di un grafo"""
    nodes_degree = [len(set(nx.neighbors(C, n))) for n in C]
    _mean_degree = sum(nodes_degree) / nx.number_of_nodes(C)
    return _mean_degree


if __name__ == "__main__":
    node_csv_path = "/home/utente/Scaricati/Tesi/index_flight.csv"
    edgelist_path = "/home/utente/Scaricati/Tesi/edgelist_2"
    infomap_path = "/home/utente/Scaricati/Tesi/infomap_clusters_2.csv"
    sp_infomap_path = "/home/utente/Scaricati/Tesi/sp_from_infomap_2.csv"
    res_directory = "/home/utente/Scaricati/Tesi/More_info/"
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
    infomap_df = pd.read_csv(infomap_path)
    sp_infomap_df = pd.read_csv(sp_infomap_path)

    # Creo le componenti, esclusa quella dei voli isolati
    infomap_components = list(components_in_graph(infomap_df[['CLUSTER', 'FLIGHTS']], F, _mapped_flights))
    sp_infomap_components = list(components_in_graph(sp_infomap_df[['GROUP_ID', 'FLIGHTS']], F, _mapped_flights))

    # Calcolo dei parametri interessanti: per infompap
    # Suppongo che la comp. dei voli isolati sia messa in fondo

    # Numero di archi interni: mi aspetto che comm. det. ne abbia molti di più
    n_of_edges_infomap = [nx.number_of_edges(C) for C in infomap_components]

    # Densità: legato al parametro precedente me la aspetto più alta su comm. det.
    density_infomap = [nx.density(C) for C in infomap_components]

    # Grado medio dei nodi: "figlio" del parametro precedente, mi aspetto la stessa cosa del numero di archi
    mean_degree_infomap = [mean_degree(C) for C in infomap_components]

    # Numero delle componenti connesse all'interno della componente: per comm. dect. mi aspetto sempre 1 a differenza
    # dello spectral part.
    connected_comp_infomap = [nx.number_connected_components(C) for C in infomap_components]

    # Autovalore di Fiedler: quanto è difficile da da dividere quella componente? Me lo aspetto più alto per comm. det.
    # Potrebbe volerci un bel po' di tempo per calcolarlo
    fiedler_eigevalue_infomap = [nx.algebraic_connectivity(C, method='lanczos') for C in infomap_components]

    # Creo i df che salverò
    infomap_columns = {'CLUSTER': infomap_df['CLUSTER'],
                       'DENSITY': density_infomap,
                       'MEAN_DEGREE': mean_degree_infomap,
                       'CONNECTED_COMP': connected_comp_infomap,
                       'FIEDLER_EIGENVALUE': fiedler_eigevalue_infomap}

    res_infomap_df = pd.DataFrame(infomap_columns)

    res_infomap_df.to_csv(res_directory + 'info_infomap_2.csv', header=True, index=False)

    # Calcolo dei parametri interessanti: per sp_louvain
    # Suppongo che la comp. dei voli isolati sia messa in fondo

    # Numero di archi interni: mi aspetto che comm. det. ne abbia molti di più
    n_of_edges_sp_infomap = [nx.number_of_edges(C) for C in sp_infomap_components]

    # Densità: legato al parametro precedente me la aspetto più alta su comm. det.
    density_sp_infomap = [nx.density(C) for C in sp_infomap_components]

    # Grado medio dei nodi: "figlio" del parametro precedente, mi aspetto la stessa cosa del numero di archi
    mean_degree_sp_infomap = [mean_degree(C) for C in sp_infomap_components]

    # Numero delle componenti connesse all'interno della componente: per comm. dect. mi aspetto sempre 1 a differenza
    # dello spectral part.
    connected_comp_sp_infomap = [nx.number_connected_components(C) for C in sp_infomap_components]

    # Autovalore di Fiedler: quanto è difficile da da dividere quella componente? Me lo aspetto più alto per comm. det.
    # Potrebbe volerci un bel po' di tempo per calcolarlo
    fiedler_eigevalue_sp_infomap = [nx.algebraic_connectivity(C, method='lanczos') for C in sp_infomap_components]

    # Creo i df che salverò
    sp_infomap_columns = {'GROUP_ID': sp_infomap_df['GROUP_ID'],
                       'DENSITY': density_sp_infomap,
                       'MEAN_DEGREE': mean_degree_sp_infomap,
                       'CONNECTED_COMP': connected_comp_sp_infomap,
                       'FIEDLER_EIGENVALUE': fiedler_eigevalue_sp_infomap}

    res_sp_infomap_df = pd.DataFrame(sp_infomap_columns)

    res_sp_infomap_df.to_csv(res_directory + 'info_sp_from_infomap_2.csv', header=True, index=False)
