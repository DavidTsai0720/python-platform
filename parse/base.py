#!/usr/bin/python
import abc
import asyncio
import random

from bs4 import BeautifulSoup
from aiohttp import ClientSession

from .setting import logging


class AsynCrawler(metaclass=abc.ABCMeta):

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    }

    def __init__(self, timeout=300, start=5, end=8):
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
    def _handler(self, param: dict):
        """
            param: {"url": url, "soup": BeautifulSoup}
        """
        raise NotImplementedError('_handler is not implement')

    async def _delay(self, start, end):
        delay = random.uniform(start, end)
        await asyncio.sleep(delay)

    async def _main(self, params: list):
        async with ClientSession() as session:
            tasks = [asyncio.create_task(self._fetch(session, param)) for param in params]
            tasks.append(asyncio.create_task(self._delay(self.start, self.end)))
            await asyncio.gather(*tasks)

    async def _fetch(self, session, param: dict):
        url = param["url"]
        logging.info(f'current url is {url}')
        async with session.get(url, headers=self.HEADERS, timeout=self.timeout) as resp:
            html = await resp.text()
            param["soup"] = BeautifulSoup(html, "html.parser")
            self._handler(param)

    def _run(self, params: list):
        """
            params: [
                {"url": https://xxxxx.xxx.xxx},
                {"url": https://xxxxx.xxx.xxxx},
            ]
        """
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._main(params))
        except Exception as e:
            logging.error(e)
