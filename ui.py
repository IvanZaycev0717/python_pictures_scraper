import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from settings import (TITLE, SIZE)

class UI(tk.Tk):
    def __init__(self, title, size):
        # Setup
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.resizable(False, False)

        self.search_frame = SearchFrame(self)
        self.search_frame.pack(pady=30)
        search_data = self.search_frame.get_entry_data()
        self.parsing_frame = ParsingFrame(self, 5)


class SearchFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.borderwidth = 10
        self.relief = tk.RIDGE

        # Grid for widgets
        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure((0, 1, 2), weight=1)

        # Variables
        self.search_data = tk.StringVar()

        self.create_widgets()

    
    def create_widgets(self):
        # create the widgets
        self.search_label = ttk.Label(self, text='Что ищем?')
        search_entry = ttk.Entry(self, textvariable=self.search_data)
        search_button = ttk.Button(self, text='Найти', command=self.get_entry_data)

        # place into the grid
        self.search_label.grid(row=0, column=0)
        search_entry.grid(row=0, column=1, columnspan=2)
        search_button.grid(row=1, column=1)
    
    def get_entry_data(self):
        return self.search_data.get()

class ParsingFrame(ttk.Frame):
    def __init__(self, parent, pictures_amount):
        super().__init__(parent)
        self.pictures_amount = pictures_amount
        self.pack()

        # Grid for widgets
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.columnconfigure((0, 1, 2), weight=1)

        # Variables
        self.pictures_amount_var = tk.IntVar(value=self.pictures_amount)
        self.folder_path_var = tk.StringVar()
        self.radio_var = tk.IntVar(value=0)
        self.status_message = tk.StringVar(value='Статус операций')

        self.create_widgets()
    
    def create_widgets(self):
        # create the widgets
        # row 0
        found_label = ttk.Label(self, text='Найдено: ')
        pictures_amount_label = ttk.Label(self, textvariable=self.pictures_amount_var)
        pictures_caption_label = ttk.Label(self, text=self.correct_pictures_label_grammar())

        # row 1
        path_label = ttk.Label(self, text='Путь сохранения: ')
        path_entry = ttk.Entry(self, textvariable=self.folder_path_var)
        path_button = ttk.Button(self, text='...', command=self.open_folder_dialog)

        # row 2
        size_label = ttk.Label(self, text='Размер: ')
        small_size_radio = ttk.Radiobutton(self, text='Маленький', value=0, variable=self.radio_var)
        big_size_radio = ttk.Radiobutton(self, text='Большой', value=1, variable=self.radio_var)

        # row 3
        how_many_label = ttk.Label(self, text='Сколько картинок: ')
        pictures_spin_box = ttk.Spinbox(self, from_=1, to=self.pictures_amount)

        # row 4
        begin_button = ttk.Button(self, text='Начать')

        # row 5
        progress_bar = ttk.Progressbar(self)

        # row 6
        status_message_label = ttk.Label(self, textvariable=self.status_message)

        # row 7
        author_label = ttk.Label(self, text='github.com/IvanZaycev0717')


        # place into the grid
        # row 0
        found_label.grid(row=0, column=0)
        pictures_amount_label.grid(row=0, column=1)
        pictures_caption_label.grid(row=0, column=2)

        # row 1
        path_label.grid(row=1, column=0)
        path_entry.grid(row=1, column=1)
        path_button.grid(row=1, column=2)

        # row 2
        size_label.grid(row=2, column=0)
        small_size_radio.grid(row=2, column=1)
        big_size_radio.grid(row=2, column=2)

        # row 3
        how_many_label.grid(row=3, column=0)
        pictures_spin_box.grid(row=3, column=1)

        # row 4
        begin_button.grid(row=4, column=1)

        # row 5
        progress_bar.grid(row=5, column=0, columnspan=3)

        # row 6
        status_message_label.grid(row=6, column=0, columnspan=3)

        # row 7
        author_label.grid(row=7, column=2)




    def open_folder_dialog(self):
        folder_path = filedialog.askdirectory()
        self.folder_path_var.set(folder_path)

    def correct_pictures_label_grammar(self):
        match self.pictures_amount:
            case 1: return 'картинка'
            case 2 | 3 | 4: return 'картинки'
            case _: return 'картинок'




if __name__ == '__main__':
    app = UI(TITLE, SIZE)
    app.mainloop()