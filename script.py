#!/usr/bin/python3
from argparse import ArgumentParser
from datetime import datetime

import parse

parser = ArgumentParser()
parser.add_argument("--get", type=str, help="exec script")
args = parser.parse_args()
CLASSOBJ = {
    "mtx": parse.MTX,
    "stock": parse.Stock,
    "code": parse.Code,
}

if __name__ == '__main__':
    obj = CLASSOBJ[args.get]
    obj.run()
