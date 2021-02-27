#!/usr/bin/python
import os
import re

import pandas as pd

from .config import CURRENTDIR

cur = os.path.join(CURRENTDIR, "mtx")
REPLACE = re.compile(r"\s")
COLUMNS = {0: "date", 1:"code", 2:"target", 3:"time", 4:"price", 5:"volumn"}

class MTXHelper:

    def _files(self):
        for _, _, files in os.walk(cur):
            yield from files

    def _convert_data(self, name):
        arr = []
        with open(name, "rb") as f:
            rows = f.read().splitlines()[1:]
            for row in rows:
                arr.append(REPLACE.sub("", row.decode()).split(","))
        df = pd.DataFrame(arr).rename(columns=COLUMNS)
        res = df.loc[df["code"] == "TX"]
        for rows in res.groupby(by="date"):
            print(rows)

    def run(self):
        for name in self._files():
            self._convert_data(os.path.join(cur, name))
            return
