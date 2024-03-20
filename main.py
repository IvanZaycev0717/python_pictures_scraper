import asyncio
from asyncio import AbstractEventLoop
from queue import Queue
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from threading import Thread
from typing import Callable

from picture_parser import PictureLinksParser
from pictures_scraper import PictureScraperSaver
from settings import (TITLE, SIZE)
from validators import (is_picture_amount_correct,
                        is_saving_path_given,
                        is_pictures_amount_chosen,
                        is_pictures_amount_positive_int)


class UI(tk.Tk):
    """Main window of the app."""
    def __init__(self, title: str, size: tuple[int],
                 loop: AbstractEventLoop,
                 loop_for_saver: AbstractEventLoop) -> None:
        # Setup
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.resizable(False, False)

        # Atributes
        self.loop: AbstractEventLoop = loop
        self.loop_for_saves: AbstractEventLoop = loop_for_saver
        self.__links_array: set[str] = set()
        self.picture_name: str = ''

        # Classes instances
        self.search_frame = SearchFrame(
            parent=self,
            links_array=self.links_array,
            set_picture_name=self.set_picture_name,
            loop=self.loop,
            update_parsing_frame_data=self.update_parsing_frame_data
            )
        self.parsing_frame = ScraperFrame(
            parent=self,
            links_array=self.links_array,
            get_picture_name=self.get_picture_name,
            loop_for_saver=self.loop_for_saves)

    @property
    def links_array(self):
        return self.__links_array

    @links_array.setter
    def links_array(self, links_array):
        self.__links_array = links_array

    def update_parsing_frame_data(self) -> None:
        """Updates data in the parsing frame."""
        pictures_amount = len(self.links_array)
        self.parsing_frame.pictures_amount_var.set(pictures_amount)
        self.parsing_frame.pictures_spin_box.configure(to=pictures_amount)
        self.parsing_frame.correct_pictures_label_grammar(pictures_amount)
        self.parsing_frame.progress_bar['value'] = 0

    def set_picture_name(self, picture_name) -> None:
        """Sets name of the future pictures."""
        self.picture_name = picture_name

    def get_picture_name(self) -> None:
        """Gets name of the current pictires."""
        return self.picture_name


class SearchFrame(ttk.Frame):
    """Frame of searching data for the main window."""
    def __init__(self, parent: UI, links_array: set[str],
                 set_picture_name: Callable, loop: AbstractEventLoop,
                 update_parsing_frame_data: Callable) -> None:
        super().__init__(parent)
        self.loop: AbstractEventLoop = loop
        self.update_parsing_frame_data: Callable = update_parsing_frame_data
        self.links_array: set[str] = links_array
        self.set_picture_name: Callable = set_picture_name

        # Place the frame into the main window
        self.pack(expand=True, fill='both', pady=30)

        # Grid for widgets
        self.rowconfigure((0, 1, 2), weight=1)
        self.columnconfigure((0, 1, 2), weight=1)

        # Variables
        self.search_data = tk.StringVar()

        self.create_widgets()

    def create_widgets(self) -> None:
        """Creates widgets in the searching frame."""
        # create the widgets
        self.search_label = ttk.Label(self, text='Что ищем?')
        self.search_entry = ttk.Entry(self, textvariable=self.search_data)
        search_button = ttk.Button(
            master=self,
            text='Найти',
            command=self.get_links,
            )
        clear_button = ttk.Button(
            master=self,
            text='Очистить список',
            command=self.clear_links_array,
            )
        # place into the grid
        self.search_label.grid(row=0, column=1)
        self.search_entry.grid(row=1, column=0,
                               columnspan=3, sticky='nsew', padx=10)
        search_button.grid(row=2, column=0, pady=5)
        clear_button.grid(row=2, column=2)

    def clear_links_array(self) -> None:
        """Gets links array empty and update data."""
        self.links_array.clear()
        self.update_parsing_frame_data()

    def get_entry_data(self) -> str:
        """Returns name of the request."""
        return self.search_data.get()

    def get_links(self) -> None:
        """Creates PictureLinksParser instance to get pictures links."""
        self.set_picture_name(self.search_entry.get())
        links = PictureLinksParser(loop, self.add_links, self.get_entry_data())
        links.start()

    def add_links(self, link) -> None:
        """Adds found links in the PictureLinksParser instance."""
        self.links_array.add(link)
        self.update_parsing_frame_data()


class ScraperFrame(ttk.Frame):
    """Frame of scraper for the main window."""
    def __init__(self, parent: UI, links_array: set[str],
                 get_picture_name: Callable,
                 loop_for_saver: AbstractEventLoop) -> None:
        super().__init__(parent)
        self.links_array: set[str] = links_array
        self.loop_for_saver: AbstractEventLoop = loop_for_saver
        self.queue: Queue = Queue()
        self.refresh_ms = 25
        self.get_picture_name: Callable = get_picture_name

        # Local var
        self.load_saver: None | PictureScraperSaver = None

        # Place the frame into the main window
        self.pack(expand=True, fill='both', padx=10)

        # Grid for widgets
        self.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.columnconfigure((0, 1, 2), weight=1)

        # Variables
        self.pictures_amount_var = tk.IntVar()
        self.folder_path_var = tk.StringVar()
        self.radio_var = tk.IntVar(value=0)
        self.status_message = tk.StringVar(value='Статус операций')

        self.create_widgets()

    def create_widgets(self) -> None:
        """Creates widgets in the scraper frame."""
        # create the widgets
        found_label = ttk.Label(self, text='Найдено: ')
        pictures_amount_label = ttk.Label(
            self,
            textvariable=self.pictures_amount_var
            )
        pictures_caption_label = ttk.Label(self, text='картинок')
        path_label = ttk.Label(self, text='Путь сохранения: ')
        self.path_entry = ttk.Entry(self, textvariable=self.folder_path_var,
                                    state='readonly', width=25)
        path_button = ttk.Button(self, text='...',
                                 command=self.open_folder_dialog)
        size_label = ttk.Label(self, text='Размер: ')
        small_size_radio = ttk.Radiobutton(self, text='Маленький',
                                           value=0, variable=self.radio_var)
        big_size_radio = ttk.Radiobutton(self, text='Большой',
                                         value=1, variable=self.radio_var)
        how_many_label = ttk.Label(self, text='Сколько картинок: ')
        self.pictures_spin_box = ttk.Spinbox(self, from_=1, width=30)
        self.begin_button = ttk.Button(self, text='Начать',
                                       command=self.start_scraper)
        self.progress_bar = ttk.Progressbar(self, orient='horizontal',
                                            mode='determinate')
        status_message_label = ttk.Label(self,
                                         textvariable=self.status_message)
        author_label = ttk.Label(self, text='github.com/IvanZaycev0717')

        # place into the grid
        found_label.grid(row=0, column=0, pady=10)
        pictures_amount_label.grid(row=0, column=1)
        pictures_caption_label.grid(row=0, column=2)
        path_label.grid(row=1, column=0, pady=10)
        self.path_entry.grid(row=1, column=1)
        path_button.grid(row=1, column=2)
        size_label.grid(row=2, column=0, pady=10)
        small_size_radio.grid(row=2, column=1)
        big_size_radio.grid(row=2, column=2)
        how_many_label.grid(row=3, column=0, pady=10)
        self.pictures_spin_box.grid(row=3, column=1, columnspan=2, ipadx=10)
        self.begin_button.grid(row=4, column=1, pady=5, sticky='w')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky='nswe')
        status_message_label.grid(row=6, column=0, columnspan=3, pady=5)
        author_label.grid(row=7, column=0)

    def start_scraper(self) -> None:
        """Validates data and starts pictures scrapping."""
        pictures_spin_amount = 0 if not self.pictures_spin_box.get() \
            else int(self.pictures_spin_box.get())
        picture_name = self.get_picture_name()
        if not is_saving_path_given(self.path_entry.get()):
            self.status_message.set('Не выбран путь сохранения')
        elif not is_pictures_amount_chosen(pictures_spin_amount):
            self.status_message.set('Не выбрано число картинок для сохранения')
        elif not is_pictures_amount_positive_int(pictures_spin_amount):
            self.status_message.set('Число картинок не может быть нулевым')
        elif not is_picture_amount_correct(pictures_spin_amount,
                                           self.links_array):
            self.status_message.set(
                f'Число картинок не может превышать {len(self.links_array)}'
                )
        else:
            self.status_message.set('')
            self.total_requests = int(self.pictures_spin_box.get())
            pictures_mode = self.radio_var.get()
            save_path = self.path_entry.get()
            if pictures_mode:
                self.get_array_of_big_pictures()
            if self.load_saver is None:
                self.begin_button['text'] = 'Отмена'
                self.status_message.set('Выполняется сохранение...')
                saver = PictureScraperSaver(
                    loop=self.loop_for_saver,
                    links_array=self.links_array,
                    picture_name=picture_name,
                    save_path=save_path,
                    total_requests=self.total_requests,
                    callback=self.update_queue)
                self.after(self.refresh_ms, self.check_queue)
                saver.start()
                self.load_saver = saver
            else:
                self.status_message.set('Операция отменена')
                self.load_saver.cancel()
                self.load_saver = None
                self.begin_button['text'] = 'Начать'

    def update_progress_bar(self, progress_percent: int) -> None:
        """Updates progress bar in the scrapping frame."""
        if progress_percent == 100:
            self.progress_bar['value'] = 100
            self.load_saver = None
            self.status_message.set('Картинки успешно сохранены')
            self.links_array.clear()
            pictures_amount = len(self.links_array)
            self.pictures_amount_var.set(pictures_amount)
            self.pictures_spin_box.configure(to=pictures_amount)
            self.correct_pictures_label_grammar(pictures_amount)
            self.begin_button['text'] = 'Начать'
        else:
            self.progress_bar['value'] = progress_percent
            self.after(self.refresh_ms, self.check_queue)

    def update_queue(self, completed_requests: int,
                     total_requests: int) -> None:
        """Puts into the queue complete percent."""
        self.queue.put(int(completed_requests * 100 / total_requests))

    def check_queue(self) -> None:
        """Check queue content and refreshes progress bar."""
        if not self.queue.empty():
            percent_complete = self.queue.get()
            self.update_progress_bar(percent_complete)
        else:
            if self.load_saver:
                if self.total_requests > 1:
                    self.after(self.refresh_ms, self.check_queue)
                else:
                    self.after(self.refresh_ms, self.check_queue)
                    self.update_progress_bar(100)

    def get_array_of_big_pictures(self) -> None:
        """Changes small size of the pictures into a big one."""
        for link in self.links_array:
            if '_n.jpg' in link:
                new_link = link.replace('_n.jpg', '_b.jpg')
                self.links_array.add(new_link)
                self.links_array.remove(link)
            elif '_m.jpg' in link:
                new_link = link.replace('_m.jpg', '_b.jpg')
                self.links_array.add(new_link)
                self.links_array.remove(link)

    def open_folder_dialog(self) -> None:
        """Allows users to chose a saving path."""
        folder_path = filedialog.askdirectory()
        self.folder_path_var.set(folder_path)

    def correct_pictures_label_grammar(self, pictures_amount: int) -> str:
        """Corrects grammar in Russian."""
        match pictures_amount:
            case 1: return 'картинка'
            case 2 | 3 | 4: return 'картинки'
            case _: return 'картинок'


class ThreadedEventLoop(Thread):
    """Additional thread for the main thread."""
    def __init__(self, loop: AbstractEventLoop):
        super().__init__()
        self._loop: AbstractEventLoop = loop
        self.daemon: bool = True

    def run(self) -> None:
        """Runs async loop."""
        self._loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop_for_saver = asyncio.new_event_loop()

    asyncio_thread = ThreadedEventLoop(loop)
    asyncio_thread.start()

    asyncio_thread_saver = ThreadedEventLoop(loop_for_saver)
    asyncio_thread_saver.start()

    app = UI(TITLE, SIZE, loop, loop_for_saver)
    app.mainloop()
