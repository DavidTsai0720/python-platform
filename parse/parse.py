from io import BytesIO
from zipfile import ZipFile
from collections import defaultdict
import json
import os.path
import re

import requests
from bs4 import BeautifulSoup

from .config import Time, DownloadMTX, CURRENTDIR
from .setting import logging
from .base import AsynCrawler

DATE = re.compile(r'\d{4}_\d{2}_\d{2}')


class MTX:

    SAVEDIR = CURRENTDIR + 'mtx/'

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
                z.extractall(cls.SAVEDIR)
            return True

    @classmethod
    def parse(cls):
        if not os.path.exists(cls.SAVEDIR):
            os.makedirs(cls.SAVEDIR)
        for date in cls._valid_dates():
            name = "Daily_" + date + ".csv"
            filename = cls.SAVEDIR + name
            if os.path.exists(filename):
                logging.warning(f"{name} is exists.")
            elif cls._save(date):
                logging.info(f"svae {name}.")
            else:
                logging.error(f"svae {name} error.")


class Code(AsynCrawler):

    links = [
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2",
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4",
    ]
    timeout = 600
    SAVEDIR = CURRENTDIR + '/code/'

    def _save(self, fileName, info):
        if not os.path.exists(self.SAVEDIR):
            os.makedirs(self.SAVEDIR)
        name = self.SAVEDIR + f'{fileName}'
        with open(name, 'wb') as f:
            f.write(json.dumps(info).encode())

    def _handler(self, soup):
        mymap = defaultdict(dict)
        fileName = ""
        for row in soup.find_all('tr'):
            arr = [r.text for r in row.find_all('td')]
            try:
                CFICode = arr[5]
                name = arr[0]
                date = arr[2]
                fileName = arr[3]
            except IndexError:
                msg = f'current arr is {arr}'
                logging.error(msg)
            except Exception as e:
                msg = f'{e}\narr is {arr}'
                logging.error(msg)
            else:
                mymap[CFICode][name] = date
        self._save(fileName, mymap)

    def run(self):
        self._run(self.links)
