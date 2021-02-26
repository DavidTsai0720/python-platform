import abc
import asyncio
import random

from bs4 import BeautifulSoup
from aiohttp import ClientSession

from .setting import logging


class AsynCrawler(metaclass=abc.ABCMeta):

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
    }

    def __init__(self, timeout=5, start=5, end=8):
        self._timeout = timeout
        self._start = start
        self._end = end

    @property
    def timeout(self):
        return self._timeout

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @abc.abstractmethod
    def _handler(self):
        raise NotImplementedError('_handler is not implement')

    async def _delay(self, start, end):
        delay = random.uniform(start, end)
        await asyncio.sleep(delay)

    async def _main(self, links):
        async with ClientSession() as session:
            tasks = [asyncio.create_task(self._fetch(row, session)) for row in links]
            tasks.append(asyncio.create_task(self._delay(self.start, self.end)))
            await asyncio.gather(*tasks)

    async def _fetch(self, url, session):
        logging.info(f'url is {url}')
        async with session.get(url, headers=self.HEADERS, timeout=self.timeout) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            self._handler(soup)

    def _run(self, links):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main(links))
