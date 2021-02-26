from datetime import date
import re
import os
import json

from .config import CURRENTDIR


class Stock:

    resource = os.path.join(CURRENTDIR, "code")

    def __init__(self):
        mymap = {}
        for _, _, names in os.walk(self.resource):
            for name in names:
                path = os.path.join(self.resource, name)
                with open(path, "rb") as f:
                    mymap[name] = json.loads(f.read())
        self.mymap = mymap
    
    def run(self):
        pass
