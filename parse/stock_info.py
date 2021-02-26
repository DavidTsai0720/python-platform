from string import Template
from dateutil.relativedelta import relativedelta
import datetime
import os
import json

from .config import CURRENTDIR
from .base import AsynCrawler


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
            fileName = os.path.join(path, date.strftime("%Y-%m"))
            if date == self.datum or not os.path.exists(fileName):
                url = template.substitute({"date": dateFMT(date), "code": code})
                yield {
                    "url": url,
                    "date": date,
                    "code": code,
                    "fileName": fileName,
                    "name": name,
                }
            date += relativedelta(months=1)

    def _candidate(self, name):
        for row in self.mymap[name]:
            yield from self._generate_dates(row, name)

    def _handler(self):
        return None

    def run(self):
        twses = self._candidate(self.twse)
        tpexs = self._candidate(self.tpex)
        links = []
        while twses or tpexs:
            link1 = next(twses, None)
            link2 = next(tpexs, None)
            if link1 is None and link2 is None:
                break
            for link in (link1, link2):
                if link is not None:
                    links.append(link)
            self._run(links)
            links.clear()
