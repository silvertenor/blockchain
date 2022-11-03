from .loadContract import *
from .updateChain import *
import xml.etree.ElementTree as ET
import random
import re

LOG_TXT_PATH = "./source/logfiles/workstationLog.txt"
DEVICE_XML_PATH = "./source/logfiles/Device.xml"
MAKO_TCW_PATH = "./source/logfiles/makoTest2.tcw"


def changeFile():
    with open(DEVICE_XML_PATH, "r") as file:
        lines = file.readlines()
    newFileLines = []
    for line in lines:
        if "IPAddress" in line:
            ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
            currentIP = re.findall(r"[0-9]+(?:\.[0-9]+){3}", line)
            for IP in currentIP:
                line = line.replace(IP, ip)
        newFileLines.append(line)
    with open(DEVICE_XML_PATH, "w") as file:
        file.writelines(newFileLines)
