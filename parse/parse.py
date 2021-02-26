from io import BytesIO
from zipfile import ZipFile
from collections import defaultdict
from string import Template
import json
import os.path
import re

import requests
from bs4 import BeautifulSoup

from .config import Time, CURRENTDIR
from .setting import logging
from .base import AsynCrawler

DATE = re.compile(r'\d{4}_\d{2}_\d{2}')


class MTX:

    SAVEDIR = CURRENTDIR + 'mtx/'
    URL = "https://www.taifex.com.tw/cht/3/dlFutPrevious30DaysSalesData"
    SRC = Template(
        "https://www.taifex.com.tw/file/taifex/Dailydownload/"
        "DailydownloadCSV/Daily_$date.zip"
    )

    def _get_dates(self):
        with requests.get(self.URL) as resp:
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all(id="button7"):
                text = link.get(key="onclick")
                m = DATE.search(text)
                if m is not None:
                    yield m.group()

    def _save(self, date):
        url = self.SRC.substitute({"date": date})
        with requests.get(url) as resp:
            with ZipFile(BytesIO(resp.content)) as z:
                z.extractall(self.SAVEDIR)

    def run(self):
        if not os.path.exists(self.SAVEDIR):
            os.makedirs(self.SAVEDIR)
        for date in self._get_dates():
            name = "Daily_" + date + ".csv"
            filename = self.SAVEDIR + name
            if os.path.exists(filename):
                logging.warning(f"{name} is exists.")
                continue
            self._save(date)
            Time.delay()


class Code(AsynCrawler):

    links = [
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2",
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4",
    ]
    timeout = 600
    SAVEDIR = CURRENTDIR + '/code/'

    def _save(self, fileName, info):
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
        if not os.path.exists(self.SAVEDIR):
            os.makedirs(self.SAVEDIR)
        self._run(self.links)
