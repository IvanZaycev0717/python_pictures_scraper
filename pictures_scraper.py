import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import Future
from http import HTTPStatus
import logging
from typing import Callable

from aiohttp import ClientSession


class PictureScraperSaver:
    """Class for pictures scraper and saver."""
    def __init__(self, loop: AbstractEventLoop, links_array: set[str],
                 picture_name: str, save_path: str,
                 total_requests: int, callback: Callable) -> None:
        self._loop: AbstractEventLoop = loop
        self._load_saver_future: Future = None
        self.links_array: set[str] = links_array
        self.completed_requests: int = 0
        self.total_requests: int = total_requests
        self.picture_name: str = picture_name
        self.save_path: str = save_path
        self.callback: Callable = callback
        self.refresh_rate: int = self.refresh_rate_corrector()

    def start(self) -> None:
        """Runs requests to handle in threadsafe mode."""
        future = asyncio.run_coroutine_threadsafe(
            self._make_requests(), self._loop
            )
        self._load_saver_future = future

    def cancel(self) -> None:
        """Cancels all pending requests."""
        if self._load_saver_future:
            self._loop.call_soon_threadsafe(self._load_saver_future.cancel)

    async def _save_image(self, session: ClientSession, url: str) -> None:
        """Asynchronously downloads the image and saves it on disk."""
        try:
            response = await session.get(url)
            if response.status == HTTPStatus.OK:
                image_data = await response.read()
                pic_file = f'{self.picture_name}{self.completed_requests}'
                with open(f'{self.save_path}/{pic_file}.jpg', 'wb') as file:
                    file.write(image_data)
                logging.info(f'Успешное сохранение картинки {url}')
            else:
                logging.error(
                    f'Ошибка при работе с картинкой {response.status}'
                    )
        except Exception as e:
            logging.exception(
                f"Ошибка при загрузке {url}: {response.status} {e}"
                )
        self.completed_requests += 1
        if self.completed_requests % self.refresh_rate == 0 or \
                self.completed_requests == self.total_requests:
            self.callback(self.completed_requests, self.total_requests)

    async def _make_requests(self) -> None:
        """Concurrently sends URL links to perform."""
        async with ClientSession() as session:
            reqs = []
            for _ in range(self.total_requests):
                current_link = self.links_array.pop()
                reqs.append(self._save_image(session, current_link))
            await asyncio.gather(*reqs)

    def refresh_rate_corrector(self) -> int:
        """Correts refresher rate."""
        if 1 < self.total_requests < 100:
            return 1
        elif 100 <= self.total_requests < 1000:
            return self.total_requests // 10
        else:
            return self.total_requests // 100
