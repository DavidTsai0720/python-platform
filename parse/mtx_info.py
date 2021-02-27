from io import BytesIO
from zipfile import ZipFile
from string import Template
import os.path
import re

import requests
from bs4 import BeautifulSoup

from .config import Time, CURRENTDIR

DATE = re.compile(r"\d{4}_\d{2}_\d{2}")


class MTX:

    SAVEDIR = CURRENTDIR + "mtx/"
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
                continue
            self._save(date)
            Time.delay()
