import json
import os.path
import re

from .config import CURRENTDIR
from .setting import logging
from .base import AsynCrawler


class Code(AsynCrawler):

    links = [
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2",
        "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4",
    ]
    timeout = 600
    SAVEDIR = os.path.join(CURRENTDIR, "code")
    VALIDCFI = re.compile(r"^(?:ESV|CEO|EDS|CBC)[A-Z]+$")
    CODENAME = re.compile(r"\s")

    def _save(self, fileName, info):
        name = os.path.join(self.SAVEDIR, fileName)
        with open(name, "wb") as f:
            f.write(json.dumps(info).encode())

    def is_valid_CFI(self, code):
        return self.VALIDCFI.match(code)

    def _handler(self, soup):
        fileName = ""
        results = []
        for row in soup.find_all("tr"):
            arr = [r.text for r in row.find_all("td")]
            try:
                CFICode = arr[5]
                code, *name = self.CODENAME.split(arr[0])
                date = arr[2]
                fileName = arr[3]
            except IndexError:
                msg = f"current arr is {arr}"
                logging.error(msg)
            except Exception as e:
                msg = f"{e}\narr is {arr}"
                logging.error(msg)
            else:
                if self.is_valid_CFI(CFICode):
                    results.append({
                        "code": code,
                        "name": ''.join(name),
                        "date": date,
                    })
        self._save(fileName, results)

    def run(self):
        if not os.path.exists(self.SAVEDIR):
            os.makedirs(self.SAVEDIR)
        self._run(self.links)
