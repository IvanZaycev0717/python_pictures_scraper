import asyncio
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from threading import Thread

from settings import (TITLE, SIZE)
from picture_links_parser import LinksGetter
from validators import is_picture_amount_correct, is_saving_path_given, is_pictures_amount_chosen, is_pictures_amount_positive_int

class UI(tk.Tk):
    def __init__(self, title, size, loop):
        # Setup
        super().__init__()
        self.loop = loop
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.resizable(False, False)

        # Atributes
        self.__links_array = set()

        # Classes instances
        self.search_frame = SearchFrame(self, self.links_array, self.loop, self.update_parsing_frame_data)
        self.search_frame.pack(pady=30)
        self.parsing_frame = ParsingFrame(self, self.links_array)

    def update_parsing_frame_data(self):
        pictures_amount = len(self.links_array)
        self.parsing_frame.pictures_amount_var.set(pictures_amount)
        self.parsing_frame.pictures_spin_box.configure(to=pictures_amount)
        self.parsing_frame.correct_pictures_label_grammar(pictures_amount)
    
    @property
    def links_array(self):
        return self.__links_array
    
    @links_array.setter
    def links_array(self, links_array):
        self.__links_array = links_array


class SearchFrame(ttk.Frame):
    def __init__(self, parent, links_array, loop, update_parsing_frame_data):
        super().__init__(parent)
        self.loop = loop
        self.update_parsing_frame_data = update_parsing_frame_data
        self.links_array = links_array

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
        search_button = ttk.Button(
            master=self,
            text='Найти',
            command=self.get_links,
            )

        # place into the grid
        self.search_label.grid(row=0, column=0)
        search_entry.grid(row=0, column=1, columnspan=2)
        search_button.grid(row=1, column=1)
    
    def get_entry_data(self):
        return self.search_data.get()

    def get_links(self):
        links = LinksGetter(loop, self.add_links, self.get_entry_data())
        links.start()

    def add_links(self, link):
        self.links_array.add(link)
        self.update_parsing_frame_data()


class ParsingFrame(ttk.Frame):
    def __init__(self, parent, links_array):
        super().__init__(parent)
        self.links_array = links_array
        self.pack()

        # Grid for widgets
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.columnconfigure((0, 1, 2), weight=1)

        # Variables
        self.pictures_amount_var = tk.IntVar()
        self.folder_path_var = tk.StringVar()
        self.radio_var = tk.IntVar(value=0)
        self.status_message = tk.StringVar(value='Статус операций')

        self.create_widgets()
    
    def create_widgets(self):
        # create the widgets
        found_label = ttk.Label(self, text='Найдено: ')
        pictures_amount_label = ttk.Label(self, textvariable=self.pictures_amount_var)
        pictures_caption_label = ttk.Label(self, text='картинок')
        path_label = ttk.Label(self, text='Путь сохранения: ')
        self.path_entry = ttk.Entry(self, textvariable=self.folder_path_var, state='readonly')
        path_button = ttk.Button(self, text='...', command=self.open_folder_dialog)
        size_label = ttk.Label(self, text='Размер: ')
        small_size_radio = ttk.Radiobutton(self, text='Маленький', value=0, variable=self.radio_var)
        big_size_radio = ttk.Radiobutton(self, text='Большой', value=1, variable=self.radio_var)
        how_many_label = ttk.Label(self, text='Сколько картинок: ')
        self.pictures_spin_box = ttk.Spinbox(self, from_=1)
        begin_button = ttk.Button(self, text='Начать', command=self.start_parsing)
        progress_bar = ttk.Progressbar(self)
        status_message_label = ttk.Label(self, textvariable=self.status_message)
        author_label = ttk.Label(self, text='github.com/IvanZaycev0717')

        # place into the grid
        found_label.grid(row=0, column=0)
        pictures_amount_label.grid(row=0, column=1)
        pictures_caption_label.grid(row=0, column=2)
        path_label.grid(row=1, column=0)
        self.path_entry.grid(row=1, column=1)
        path_button.grid(row=1, column=2)
        size_label.grid(row=2, column=0)
        small_size_radio.grid(row=2, column=1)
        big_size_radio.grid(row=2, column=2)
        how_many_label.grid(row=3, column=0)
        self.pictures_spin_box.grid(row=3, column=1)
        begin_button.grid(row=4, column=1)
        progress_bar.grid(row=5, column=0, columnspan=3)
        status_message_label.grid(row=6, column=0, columnspan=3)
        author_label.grid(row=7, column=2)
    
    def start_parsing(self):
        pictures_spin_amount = 0 if not self.pictures_spin_box.get() else int(self.pictures_spin_box.get())
        if not is_saving_path_given(self.path_entry.get()):
            self.status_message.set('Не выбран путь сохранения')
        elif not is_pictures_amount_chosen(pictures_spin_amount):
            self.status_message.set('Не выбрано число картинок для сохранения')
        elif not is_pictures_amount_positive_int(pictures_spin_amount):
            self.status_message.set('Число картинок не может быть нулевым')
        elif not is_picture_amount_correct(pictures_spin_amount, self.links_array):
            self.status_message.set(f'Число картинок не может превышать {len(self.links_array)}')
        else:
            print('else')

    def open_folder_dialog(self):
        folder_path = filedialog.askdirectory()
        self.folder_path_var.set(folder_path)

    def correct_pictures_label_grammar(self, pictures_amount):
        match pictures_amount:
            case 1: return 'картинка'
            case 2 | 3 | 4: return 'картинки'
            case _: return 'картинок'


class ThreadedEventLoop(Thread):
    def __init__(self, loop):
        super().__init__()
        self._loop = loop
        self.daemon = True

    def run(self):
        self._loop.run_forever()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    asyncio_thread = ThreadedEventLoop(loop)
    asyncio_thread.start()

    app = UI(TITLE, SIZE, loop)
    app.mainloop()
