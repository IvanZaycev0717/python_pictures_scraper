import aiohttp
import asyncio

from bs4 import BeautifulSoup

from settings import PHOTO_CONTAINER, PHOTO_CLASS, URL


class LinksGetter:
    def __init__(self, loop, add_links, search_word) -> None:
        self._get_links_future = None
        self._loop = loop
        self.add_links = add_links
        self.url = rf'{URL + search_word}'

    def start(self):
        future = asyncio.run_coroutine_threadsafe(self.get_html(), self._loop)
        self._get_links_future = future

    def cancel(self):
        if self._get_links_future:
            self._loop.call_soon_threadsafe(self._get_links_future.cancel)

    def parse_html_to_get_links(self, html):
        soup = BeautifulSoup(html, 'lxml')
        box = soup.find_all(PHOTO_CONTAINER, class_=PHOTO_CLASS)
        for tag in box:
            img_tag = tag.find('img')
            src_value = img_tag.get('src')
            self.add_links('https:' + src_value)

    async def get_html(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                html = await response.text()
        self.parse_html_to_get_links(html)
