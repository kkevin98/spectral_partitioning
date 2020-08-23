from tkinter import *
from tkinter import ttk, filedialog, messagebox
import networkx as nx
import spectral_partitioning as sp


def _set_info_from_path(path):
    '''
    Una volta inserito il percorso di un file mostra nella status bar
    il numero di nodi della rete, se è una rete, altrimenti mostra
    un messaggio di file non valido
    '''
    G = nx.read_gpickle(path)
    is_Graph = isinstance(G, nx.Graph)
    if is_Graph:
        _status_msg.set("Il grafo scelto ha {} nodi".format(G.number_of_nodes()))
    else:
        _status_msg.set("Il file scelto non è valido...")

def select_path():
    '''
    Ottiene il nome del file da aprire
    '''
    path = filedialog.askopenfilename(initialdir="/home/utente/",
                                           filetypes=[("pickle file", "*.pickle")],
                                           title="Seleziona il grafo")
    if path:
        _classes.set(())  # Quando seleziono un file svuoto il contenuto precedente della listbox
        _set_info_from_path(path)
        _path.set(path)
        # _file_info.set(_nodes_info_from_file(file_name))



if __name__ == "__main__":
    _root = Tk()
    _root.title('Spectral partitioning app')

    _mainframe = ttk.Frame(_root, padding='5 5 5 5')
    _mainframe.grid(row=0, column=0, sticky=(E, W, N, S))

    # Per selezionare la rete
    _path_frame = ttk.LabelFrame(
        _mainframe, text='Percorso file', padding='5 5 5 5')
    _path_frame.grid(row=0, column=0, sticky=(E, W))
    _path_frame.columnconfigure(0, weight=1)  #??
    _path_frame.rowconfigure(0, weight=1)  #??

    # _welcome_lbl = ttk.Label(
    #     _path_frame, text="Scegli il file contenente il grafo")
    # _welcome_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=(W, N))

    _path = StringVar()
    _path.set('Path')
    _path_entry = ttk.Entry(
        _path_frame, width=40, textvariable=_path)
    _path_entry.grid(row=0, column=0, sticky=(E, W, S, N), padx=5)
    _path_entry.focus()  # all'avvio posiziona il cursore sul percorso del file, comando da mettere alla fine

    _get_path_btn = ttk.Button(
        _path_frame, text='Apri', command=select_path)
    _get_path_btn.grid(row=0, column=1, sticky=W, padx=5)

    # Per selezionare e visualizzare i nodi delle classi
    _class_frame = ttk.LabelFrame(
        _mainframe, text='Componenti', padding='9 0 0 0')
    _class_frame.grid(row=1, column=0, sticky=(N, S, E, W))
    # _class_frame.columnconfigure(0, weight=1)  #??
    # _class_frame.rowconfigure(0, weight=1)  #??

    _classes = StringVar()
    _class_listbox = Listbox(
        _class_frame, listvariable=_classes, height=6, width=25)
    _class_listbox.grid(row=0, column=0, sticky=(E, W), pady=5, rowspan=3)
    _scrollbar = ttk.Scrollbar(
        _class_frame, orient=VERTICAL, command=_class_listbox.yview)
    _scrollbar.grid(row=0, column=1, sticky=(S, N), pady=6, rowspan=3)
    _class_listbox.configure(yscrollcommand=_scrollbar.set)

    _choice_lbl = ttk.Label(
        _class_frame, text="Scegli il numero di nodi\ndella componente"
    )
    _choice_lbl.grid(row=0, column=2, padx=5, pady=5, sticky=(N, W))
    _number_of_nodes = StringVar()
    _number_of_nodes_entry = ttk.Entry(
        _class_frame, width=25, textvariable=_number_of_nodes
    )
    _number_of_nodes_entry.grid(row=1, column=2, sticky=(N, S, E, W), padx=5)
    _get_nodes_btn = ttk.Button(
        _class_frame, text='Aggiungi', command=None)
    _get_nodes_btn.grid(row=2, column=2, sticky=W, padx=5)

    _divide_btn = ttk.Button(  # Per avviare il partizionamento
        _mainframe, text="Dividi", command=divide_and_save
    )
    _divide_btn.grid(row=2, column=0, sticky=E, pady=5)

    # Per la status bar
    _status_frame = ttk.Frame(
        _root, relief="sunken", padding="2 2 2 2")
    _status_frame.grid(row=1, column=0, sticky=(E, W, S))
    _status_msg = StringVar()
    _status_msg.set("Seleziona il file contente la rete")
    _status = ttk.Label(
        _status_frame, textvariable=_status_msg
    )
    _status.grid(row=0, column=0, sticky=W)






    # _root.bind('<Return>', select_path)
    _root.mainloop()  # per far partire il tutto, da aggiungere alla fine
