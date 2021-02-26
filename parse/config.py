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
