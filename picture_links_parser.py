import aiohttp
import asyncio
from pprint import pprint

from bs4 import BeautifulSoup

url = rf'https://www.flickr.com/search/?text=kittens'


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
    soup = BeautifulSoup(html, 'lxml')
    box = soup.find_all('div', class_='photo-list-photo-container')
    for tag in box:
        img_tag = tag.find('img')
        src_value = img_tag.get('src')
        print(src_value)

asyncio.run(main())
