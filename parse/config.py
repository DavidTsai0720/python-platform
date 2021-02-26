from string import Template
import os.path
import time
import random

CURRENTDIR = os.path.dirname(os.path.realpath(__file__)) + '/save/'


class Time:

    start = 5
    end = 8

    @classmethod
    def delay(cls):
        sleep = random.uniform(cls.start, cls.end)
        time.sleep(sleep)


class DownloadMTX:

    _URL = "https://www.taifex.com.tw/cht/3/dlFutPrevious30DaysSalesData"
    _SRC = Template(
        "https://www.taifex.com.tw/file/taifex/Dailydownload/"
        "DailydownloadCSV/Daily_$date.zip"
    )

    @classmethod
    def csv(cls, date):
        return cls._SRC.substitute({"date": date})

    @classmethod
    def main(cls):
        return cls._URL
