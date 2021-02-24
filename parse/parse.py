from string import Template
from io import BytesIO
from zipfile import ZipFile
import logging
import re
import os.path
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    filename="mylog.log",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="w",
    format="%(levelname)s %(asctime)s: %(message)s",
)

DATE = re.compile(r'\d{4}_\d{2}_\d{2}')
SAVEDIR = os.path.dirname(os.path.realpath(__file__)) + '/save/'
SLEEP = 5


def _delay():
    time.sleep(SLEEP)


class MTX:

    URL = "https://www.taifex.com.tw/cht/3/dlFutPrevious30DaysSalesData"
    SRC = Template(
        "https://www.taifex.com.tw/file/taifex/Dailydownload/"
        "DailydownloadCSV/Daily_$date.zip"
    )

    def _valid_date(self):
        links = []
        with requests.get(self.URL) as resp:
            _delay()
            soup = BeautifulSoup(resp.text, "html.parser") if resp.ok else ""
            links = soup.find_all(id="button7")
        for link in links:
            src = link.get(key="onclick")
            m = DATE.search(src)
            if m is not None:
                yield m.group()

    def _save(self, date):
        src = self.SRC.substitute({"date": date})
        with requests.get(src) as resp:
            _delay()
            if not resp.ok:
                return False
            with ZipFile(BytesIO(resp.content)) as z:
                z.extractall(SAVEDIR)
            return True

    def parse(self):
        for date in self._valid_date():
            name = "Daily_" + date + ".csv"
            filename = SAVEDIR + name
            if os.path.exists(filename):
                logging.warning(f"{name} is exists.")
            elif self._save(date):
                logging.info(f"svae {name}.")
            else:
                logging.error(f"svae {name} error.")


if __name__ == "__main__":
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
    mtx = MTX()
    mtx.parse()
