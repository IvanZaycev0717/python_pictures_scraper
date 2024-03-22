import aiohttp
import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import Future
from typing import Callable


from bs4 import BeautifulSoup

from settings import PHOTO_CONTAINER, PHOTO_CLASS, URL


class PictureLinksParser:
    """Class for pictures links parser."""
    def __init__(self, loop: AbstractEventLoop,
                 add_links: Callable, search_word: str) -> None:
        self._get_links_future: Future = None
        self._loop: AbstractEventLoop = loop
        self.add_links: Callable = add_links
        self.url: str = rf'{URL + search_word}'

    def start(self) -> None:
        """Runs requests to handle in threadsafe mode."""
        future = asyncio.run_coroutine_threadsafe(
            self._make_request(), self._loop
            )
        self._get_links_future = future

    def cancel(self) -> None:
        """Cancels all pending requests."""
        if self._get_links_future:
            self._loop.call_soon_threadsafe(self._get_links_future.cancel)

    def _add_links(self, html: str) -> None:
        """Parses HTML and adds links to the array."""
        soup = BeautifulSoup(html, 'lxml')
        box = soup.find_all(PHOTO_CONTAINER, class_=PHOTO_CLASS)
        for tag in box:
            img_tag = tag.find('img')
            src_value = img_tag.get('src')
            self.add_links('https:' + src_value)

    async def _make_request(self) -> None:
        """Downloads HTML with pictures links."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                html = await response.text()
        self._add_links(html)
