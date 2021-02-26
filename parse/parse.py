from io import BytesIO
from zipfile import ZipFile
import os.path
import asyncio
import re

import requests
from bs4 import BeautifulSoup
from aiohttp import ClientSession

from .config import Time, DownloadMTX, CURRENTDIR
from .setting import logging

DATE = re.compile(r'\d{4}_\d{2}_\d{2}')
SAVEDIR = CURRENTDIR + 'mtx/'


class MTX:

    @classmethod
    def _valid_dates(cls):
        links = []
        with requests.get(DownloadMTX.main()) as resp:
            soup = BeautifulSoup(resp.text, "html.parser") if resp.ok else ""
            links = soup.find_all(id="button7")
        for link in links:
            text = link.get(key="onclick")
            m = DATE.search(text)
            if m is not None:
                yield m.group()

    @classmethod
    def _save(cls, date):
        url = DownloadMTX.csv(date)
        with requests.get(url) as resp:
            Time.delay()
            if not resp.ok:
                return False
            with ZipFile(BytesIO(resp.content)) as z:
                z.extractall(SAVEDIR)
            return True

    @classmethod
    def parse(cls):
        for date in cls._valid_dates():
            name = "Daily_" + date + ".csv"
            filename = SAVEDIR + name
            if os.path.exists(filename):
                logging.warning(f"{name} is exists.")
            elif cls._save(date):
                logging.info(f"svae {name}.")
            else:
                logging.error(f"svae {name} error.")


async def main():
    links = []
    async with ClientSession() as session:
        tasks = [asyncio.create_task(fetch(link, session)) for link in links]
        await asyncio.gather(*tasks)


async def fetch(link, session):
    async with session.get(link) as resp:
        html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")

# loop = asyncio.get_event_loop()  #建立事件迴圈(Event Loop)
# loop.run_until_complete(main())  #執行協程(coroutine)