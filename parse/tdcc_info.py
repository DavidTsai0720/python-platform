import os
import json

from bs4 import BeautifulSoup
import requests

from .config import CURRENTDIR
from .base import AsynCrawler


class TDCC(AsynCrawler):

    savePath = os.path.join(CURRENTDIR, "tdcc")

    @property
    def url(self):
        try:
            return self._url
        except AttributeError:
            self._url = "https://www.tdcc.com.tw/smWeb/QryStockAjax.do"
            return self._url

    async def _fetch(self, session, param: dict):
        payload = param["payload"]
        url = param["url"]
        async with session.post(
            url,
            headers=self.HEADERS,
            data=payload,
            timeout=self.timeout
        ) as resp:
            html = await resp.text()
            param["soup"] = BeautifulSoup(html, "html.parser")
            self._handler(param)

    @property
    def dates(self):
        try:
            return self._dates
        except AttributeError:
            payload = {"REQ_OPR": "qrySelScaDates"}
            with requests.post(
                self.url,
                headers=self.HEADERS,
                data=payload
            ) as resp:
                dates = resp.json()
            self._dates = sorted(dates)
            return self._dates

    def _handler(self, param: dict):
        data = []
        for row in param["soup"].find_all("tr"):
            arr = [r.text for r in row.find_all("td")]
            if len(arr) != 5:
                continue
            order = arr[0]
            level = arr[1]
            people = arr[2]
            shares = arr[3]
            percentage = arr[4]
            data.append({
                "order": order,
                "level": level,
                "people": people,
                "shares": shares,
                "percentage": percentage
            })
        file_name = os.path.join(self.savePath, param["code"], param["date"])
        self._save(file_name, data)

    @property
    def stockinfo(self):
        try:
            return self._stockinfo
        except AttributeError:
            path = os.path.join(CURRENTDIR, "code")
            for root, _, files in os.walk(path):
                pass
            arr = []
            for file in files:
                name = os.path.join(path, file)
                with open(name, "rb") as f:
                    arr.append(json.loads(f.read().decode()))
            self._stockinfo = arr
            return self._stockinfo

    def has_exists(self, code, date):
        dirname = os.path.join(self.savePath, code)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            return False
        file_name = os.path.join(dirname, date)
        if not os.path.exists(file_name):
            return False
        if os.path.getsize(file_name) < 3:
            return False
        return True

    def _candidates(self):
        for date in self.dates:
            for stocks in self.stockinfo:
                for stock in stocks:
                    created = stock["date"].replace("/", "")
                    current, created = map(int, (date, created))
                    if current < created:
                        continue
                    if self.has_exists(stock["code"], date):
                        continue
                    yield {
                        "code": stock["code"],
                        "date": date,
                    }

    def run(self) -> None:
        if not os.path.exists(self.savePath):
            os.makedirs(self.savePath)
        payload = {
            "SqlMethod": "StockNo",
            "StockName": "",
            "REQ_OPR": "SELECT",
            "clkStockName": "",
        }
        for candidate in self._candidates():
            date = candidate["date"]
            code = candidate["code"]
            payload["scaDates"] = date
            payload["scaDate"] = date
            payload["StockNo"] = code
            payload["clkStockNo"] = code
            param = {
                "payload": payload,
                "url": self.url,
                "date": date,
                "code": code
            }
            self._run([param])
