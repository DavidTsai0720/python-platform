#!/usr/bin/python3
from argparse import ArgumentParser

import parse

parser = ArgumentParser()
parser.add_argument("--get", type=str, help="exec script")
args = parser.parse_args()
CLASSOBJ = {
    "mtx": parse.MTX,
    "stock": parse.Stock,
    "code": parse.Code,
    "tdcc": parse.TDCC,
}

if __name__ == '__main__':
    obj = CLASSOBJ[args.get]()
    obj.run()
