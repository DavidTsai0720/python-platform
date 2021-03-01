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
            datum = datetime.date.today()
            self._datum = datetime.date(datum.year, datum.month, 1)
            return self._datum

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

    def is_valid(self, file_name, date):
        if not os.path.exists(file_name):
            return True
        if os.path.getsize(file_name) < 3:
            return True
        if date >= self.datum - relativedelta(months=1):
            return True
        return False

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
            if self.is_valid(file_name, date):
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

    @property
    def errorLog(self):
        try:
            return self._errorLog
        except AttributeError:
            self._errorLog = os.path.join(self.savePath, "other")
            return self._errorLog

    def _save(self, data, file_name):
        with open(file_name, "wb") as f:
            f.write(json.dumps(data).encode())

    def _handler(self, param: dict):
        data = []
        for row in param["soup"].find_all("tr"):
            info = [r.text for r in row.find_all("td")]
            try:
                yy, mm, dd = info[0].split('/')
                while not dd.isdigit():
                    dd = dd[:-1]
                yy, mm, dd = map(int, (yy, mm, dd))
                date = datetime.date(yy+1911, mm, dd).strftime("%Y-%m-%d")
                volumn = info[1]
                OPEN = info[3]
                HIGH = info[4]
                LOW = info[5]
                CLOSE = info[6]
            except Exception as e:
                logging.error(e)
            else:
                data.append({
                    "code": param["code"],
                    "date": date,
                    "open": OPEN,
                    "high": HIGH,
                    "low": LOW,
                    "close": CLOSE,
                    "volumn": volumn
                })
        self._save(data, param["file_name"])

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
