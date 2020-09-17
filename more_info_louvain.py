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
    edgelist_path = "/home/utente/Scaricati/Tesi/edgelist_3"
    louvain_path = "/home/utente/Scaricati/Tesi/Louvain_3.csv"
    sp_louvain_path = "/home/utente/Scaricati/Tesi/sp_from_louvain.csv"
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
    louvain_df = pd.read_csv(louvain_path)
    sp_louvain_df = pd.read_csv(sp_louvain_path)

    # Creo le componenti
    louvain_components = list(components_in_graph(louvain_df[['MOD_CLASS', 'FLIGHTS']], F, _mapped_flights))
    sp_louvain_components = list(components_in_graph(sp_louvain_df[['GROUP_ID', 'FLIGHTS']], F, _mapped_flights))

    # Calcolo dei parametri interessanti: per louvain
    # Suppongo che la comp. dei voli isolati sia messa in fondo

    # Numero di archi interni: mi aspetto che comm. det. ne abbia molti di più
    n_of_edges_louv = [nx.number_of_edges(C) for C in louvain_components]

    # Densità: legato al parametro precedente me la aspetto più alta su comm. det.
    density_louv = [nx.density(C) for C in louvain_components]

    # Grado medio dei nodi: "figlio" del parametro precedente, mi aspetto la stessa cosa del numero di archi
    mean_degree_louv = [mean_degree(C) for C in louvain_components]

    # Numero delle componenti connesse all'interno della componente: per comm. dect. mi aspetto sempre 1 a differenza
    # dello spectral part.
    connected_comp_louv = [nx.number_connected_components(C) for C in louvain_components]

    # Autovalore di Fiedler: quanto è difficile da da dividere quella componente? Me lo aspetto più alto per comm. det.
    # Potrebbe volerci un bel po' di tempo per calcolarlo
    fiedler_eigevalue_louv = [nx.algebraic_connectivity(C, method='lanczos') for C in louvain_components]

    # Creo i df che salverò
    louvain_columns = {'MOD_CLASS': louvain_df['MOD_CLASS'],
                       'DENSITY': density_louv,
                       'MEAN_DEGREE': mean_degree_louv,
                       'CONNECTED_COMP': connected_comp_louv,
                       'FIEDLER_EIGENVALUE': fiedler_eigevalue_louv}

    res_louvain_df = pd.DataFrame(louvain_columns)

    res_louvain_df.to_csv(res_directory + 'info_louvain_3.csv', header=True, index=False)

    # Calcolo dei parametri interessanti: per sp_louvain
    # Suppongo che la comp. dei voli isolati sia messa in fondo

    # Numero di archi interni: mi aspetto che comm. det. ne abbia molti di più
    n_of_edges_sp_louv = [nx.number_of_edges(C) for C in sp_louvain_components]

    # Densità: legato al parametro precedente me la aspetto più alta su comm. det.
    density_sp_louv = [nx.density(C) for C in sp_louvain_components]

    # Grado medio dei nodi: "figlio" del parametro precedente, mi aspetto la stessa cosa del numero di archi
    mean_degree_sp_louv = [mean_degree(C) for C in sp_louvain_components]

    # Numero delle componenti connesse all'interno della componente: per comm. dect. mi aspetto sempre 1 a differenza
    # dello spectral part.
    connected_comp_sp_louv = [nx.number_connected_components(C) for C in sp_louvain_components]

    # Autovalore di Fiedler: quanto è difficile da da dividere quella componente? Me lo aspetto più alto per comm. det.
    # Potrebbe volerci un bel po' di tempo per calcolarlo
    fiedler_eigevalue_sp_louv = [nx.algebraic_connectivity(C, method='lanczos') for C in sp_louvain_components]

    # Creo i df che salverò
    sp_louvain_columns = {'GROUP_ID': sp_louvain_df['GROUP_ID'],
                       'DENSITY': density_sp_louv,
                       'MEAN_DEGREE': mean_degree_sp_louv,
                       'CONNECTED_COMP': connected_comp_sp_louv,
                       'FIEDLER_EIGENVALUE': fiedler_eigevalue_sp_louv}

    res_sp_louvain_df = pd.DataFrame(sp_louvain_columns)

    res_sp_louvain_df.to_csv(res_directory + 'info_sp_from_louvain_3.csv', header=True, index=False)