from tkinter import *
from tkinter import ttk, filedialog, messagebox

def fetch_path():
    '''Ottiene il nome del file da aprire'''
    '''Ancora da fare!!'''


if __name__ == "__main__":

    _root = Tk()
    _root.title('Spectral partitioning app')

    _mainframe = ttk.Frame(_root, padding='5 5 5 5')
    _mainframe.grid(row=0, column=0, sticky=(E, W, N, S))

    _path_frame = ttk.LabelFrame(
        _mainframe, text='Percorso file', padding='5 5 5 5')
    _path_frame.grid(row=1, column=0, sticky=(E, W))
    # _position_frame.columnconfigure(0, weight=1)
    # _position_frame.rowconfigure(0, weight=1)

    _welcome_lbl = ttk.Label(
        _path_frame, text="Scegli il file contenente il grafo:")
    _welcome_lbl.grid(row=0, column=0, padx=5, pady=5, sticky=(W, N))

    _path = StringVar()
    _path.set('Path')
    _path_entry = ttk.Entry(
        _path_frame, width=40, textvariable=_path)
    _path_entry.grid(row=1, column=0, sticky=(E, W, S, N), padx=5)
    _path_entry.focus() # all'avvio posiziona il cursore sul percorso del file, da mettere alla fine

    _fetch_path_btn = ttk.Button(
        _path_frame, text='Apri', command=fetch_path) # fetch_path è una funzione che devo ancora definire
    _fetch_path_btn.grid(row=1, column=1, sticky=W, padx=5)
    _root.bind('<Return>', fetch_path)








    _root.mainloop() # per far partire il tutto, da aggiungere alla fine