from string import Template
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile
import logging
import re
import os.path
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(filename='myapp.log', level=logging.INFO)


URL = "https://www.taifex.com.tw/cht/3/dlFutPrevious30DaysSalesData"
DATE = re.compile(r'\d{4}_\d{2}_\d{2}')
KEY = "button7"
SRC = Template(
    "https://www.taifex.com.tw/file/taifex/Dailydownload/"
    "DailydownloadCSV/Daily_$date.zip"
)
SAVEDIR = os.path.dirname(os.path.realpath(__file__)) + '/save/'
SLEEP = 5


def _delay():
    time.sleep(SLEEP)


def _valid_date():
    with requests.get(URL) as resp:
        _delay()
        if not resp.ok:
            return
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all(id=KEY)
        for link in links:
            src = link.get(key="onclick")
            m = DATE.search(src)
            if m is not None:
                yield m.group()


def _save(date):
    src = SRC.substitute({'date': date})
    with requests.get(src) as resp:
        _delay()
        if not resp.ok:
            return None
        with ZipFile(BytesIO(resp.content)) as z:
            z.extractall(SAVEDIR)


def run():
    for date in _valid_date():
        filename = SAVEDIR + 'Daily_' + date + '.csv'
        if os.path.exists(filename):
            current = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"this {date} has been exists. created: {current}")
        else:
            _save(date)


if __name__ == "__main__":
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
    run()
