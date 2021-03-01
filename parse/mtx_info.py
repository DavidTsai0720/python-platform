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
    CSV = Template(
        "https://www.taifex.com.tw/file/taifex/Dailydownload/"
        "DailydownloadCSV/Daily_$date.zip"
    )
    RPT = Template(
        "https://www.taifex.com.tw/file/taifex/Dailydownload"
        "/Dailydownload/Daily_$date.zip")

    def _get_dates(self):
        with requests.get(self.URL) as resp:
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all(id="button7"):
                text = link.get(key="onclick")
                m = DATE.search(text)
                if m is not None:
                    yield m.group()

    def _save_csv(self, date):
        url = self.CSV.substitute({"date": date})
        with requests.get(url) as resp:
            with ZipFile(BytesIO(resp.content)) as z:
                z.extractall(self.SAVEDIR)

    def _save_rpt(self, date):
        url = self.RPT.substitute({"date": date})
        with requests.get(url) as resp:
            name = os.path.join(self.SAVEDIR, f"Daily_{date}.zip")
            with open(name, "wb") as f:
                f.write(BytesIO(resp.content).getvalue())

    def run(self):
        if not os.path.exists(self.SAVEDIR):
            os.makedirs(self.SAVEDIR)
        for date in self._get_dates():
            for func in (self._save_csv, self._save_rpt):
                func(date)
                Time.delay()
