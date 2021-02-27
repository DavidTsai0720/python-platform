from string import Template
from dateutil.relativedelta import relativedelta
import datetime
import os
import json

from .config import CURRENTDIR
from .base import AsynCrawler
from .setting import logging


class Stock(AsynCrawler):

    """
        twse start date is 20100101
        tpex start date is 19940101
    """
    resource = os.path.join(CURRENTDIR, "code")
    savePath = os.path.join(CURRENTDIR, "stock")

    @property
    def mymap(self):
        try:
            return self._mymap
        except AttributeError:
            mymap = {}
            for _, _, names in os.walk(self.resource):
                for name in names:
                    path = os.path.join(self.resource, name)
                    with open(path, "rb") as f:
                        mymap[name] = json.loads(f.read())
            self._mymap = mymap
            return mymap

    @property
    def datum(self):
        try:
            return self._datum
        except AttributeError:
            today = datetime.date.today()
            self._today = datetime.date(today.year, today.month, 1)
            return self._today

    @property
    def twse(self):
        return "上市"

    @property
    def tpex(self):
        return "上櫃"

    @property
    def template(self):
        try:
            return self._template
        except AttributeError:
            self._template = {
                self.twse: Template(
                    "https://www.twse.com.tw/exchangeReport/STOCK_DAY?"
                    "response=html&date=$date&stockNo=$code"
                ),
                self.tpex: Template(
                    "https://www.tpex.org.tw/web/stock/aftertrading/"
                    "daily_trading_info/st43_print.php?l=zh-tw&d=$date&stkno=$code"
                )
            }
            return self._template

    @property
    def startDate(self):
        try:
            return self._startDate
        except AttributeError:
            self._startDate = {
                self.twse: datetime.date(2010, 1, 1),
                self.tpex: datetime.date(1994, 1, 1),
            }
            return self._startDate

    @property
    def dateFMT(self):
        try:
            return self._dateFMT
        except AttributeError:
            def func(date):
                yy = date.year - 1911
                mm = date.month
                return f"{yy}/{mm}"
            self._dateFMT = {
                self.twse: lambda x: x.strftime("%Y%m%d"),
                self.tpex: func,
            }
            return self._dateFMT

    def _generate_dates(self, row, name):
        code, date = row["code"], row["date"]
        path = os.path.join(self.savePath, code)
        if not os.path.exists(path):
            os.makedirs(path)
        yy, mm, dd = map(int, date.split('/'))
        date = datetime.date(yy, mm, 1)
        startDate = self.startDate[name]
        date = date if date >= startDate else startDate
        template = self.template[name]
        dateFMT = self.dateFMT[name]
        while date <= self.datum:
            file_name = os.path.join(path, date.strftime("%Y-%m"))
            if date == self.datum or not os.path.exists(file_name):
                url = template.substitute({"date": dateFMT(date), "code": code})
                yield {
                    "url": url,
                    "date": date,
                    "code": code,
                    "file_name": file_name,
                    "name": name,
                }
            date += relativedelta(months=1)

    def _candidate(self, name):
        for row in self.mymap[name]:
            yield from self._generate_dates(row, name)

    def html_handle(self, soup):
        for row in soup.find_all("tr"):
            arr = [r.text for r in row.find_all("td")]
            try:
                yy, mm, dd = arr[0].split('/')
                while not dd.isdigit():
                    dd = dd[:-1]
                yy, mm, dd = map(int, (yy, mm, dd))
                date = datetime.date(yy+1911, mm, dd).strftime("%Y-%m-%d")
                volumn = arr[1]
                OPEN = arr[3]
                HIGH = arr[4]
                LOW = arr[5]
                CLOSE = arr[6]
            except Exception:
                msg = f"current arr is {arr}"
                logging.error(msg)
            else:
                yield {
                    "date": date,
                    "open": OPEN,
                    "high": HIGH,
                    "low": LOW,
                    "close": CLOSE,
                    "volumn": volumn
                }

    @property
    def errorLog(self):
        try:
            return self._errorLog
        except AttributeError:
            self._errorLog = os.path.join(self.savePath, "other")
            return self._errorLog

    def _handler(self, param: dict):
        arr = tuple(self.html_handle(param["soup"]))
        if len(arr) == 0:
            with open(self.errorLog, "a") as f:
                f.write(param["url"] + "\n")
            logging.warning(param["url"] + " has no information ")
            return
        file_name = param["file_name"]
        with open(file_name, "wb") as f:
            f.write(json.dumps(arr).encode())

    def run(self) -> None:
        twses = self._candidate(self.twse)
        tpexs = self._candidate(self.tpex)
        params = []
        while twses or tpexs:
            param1 = next(twses, None)
            param2 = next(tpexs, None)
            for param in (param1, param2):
                if param is not None:
                    params.append(param)
            if len(params) == 0:
                return
            self._run(params)
            params.clear()