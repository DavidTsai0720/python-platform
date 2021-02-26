import logging

logging.basicConfig(
    filename="mylog.log",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="w",
    format="%(levelname)s %(asctime)s: %(message)s",
)
