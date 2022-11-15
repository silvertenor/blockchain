import os
from .updateChain import *
from time import sleep


def main():
    while True:
        basedir = os.environ["basedir"]
        for item in os.walk(os.path.join(basedir, "source/")):
            pathToSearch = item[0]
            for file in os.scandir(pathToSearch):
                if ".xml" in file.path.lower():
                    chainChecker(file.path)
        sleep(5)
