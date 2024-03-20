import asyncio
from concurrent.futures import Future
from asyncio import AbstractEventLoop
from http import HTTPStatus
import logging
from typing import Callable, Optional
from aiohttp import ClientSession
import aiofiles


class PictureSaver:
    def __init__(self, loop, links_array, picture_name, save_path, total_requests, callback):
        self._loop = loop
        self.completed_requests = 0
        self._load_saver_future = None
        self.links_array = links_array
        self.total_requests = total_requests
        self.picture_name = picture_name
        self.save_path = save_path
        self.callback = callback
        self.refresh_rate = self.refresh_rate_corrector()
    
    def refresh_rate_corrector(self):
        if 1 < self.total_requests < 100:
            return 1
        elif 100 <= self.total_requests < 1000:
            return self.total_requests // 10
        else:
            return self.total_requests // 100
    
    def start(self):
        future = asyncio.run_coroutine_threadsafe(self._make_requests(), self._loop)
        self._load_saver_future = future

    def cancel(self):
        if self._load_saver_future:
            self._loop.call_soon_threadsafe(self._load_saver_future.cancel)
    
    async def _save_image(self, session, url):
        try:
            response = await session.get(url)
            if response.status == HTTPStatus.OK:
                image_data = await response.read()
                async with aiofiles.open(f'{self.save_path}/{self.picture_name}{self.completed_requests}.jpg', 'wb') as file:
                    await file.write(image_data)
                logging.info(f'Успешное сохранение картинки {url}')
            else:
                logging.error(f'Ошибка при работе с картинкой {response.status}')
        except Exception as e:
            logging.exception(f"Ошибка при загрузке {url}: {response.status} {e}")
        self.completed_requests += 1
        if self.completed_requests % self.refresh_rate == 0 or self.completed_requests == self.total_requests:
            self.callback(self.completed_requests, self.total_requests)


    async def _make_requests(self):
        async with ClientSession() as session:
            reqs = []
            for _ in range(self.total_requests):
                current_link = self.links_array.pop()
                reqs.append(self._save_image(session, current_link))
            await asyncio.gather(*reqs)
