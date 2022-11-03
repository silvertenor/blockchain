from .loadContract import *
from .updateChain import *
import xml.etree.ElementTree as ET

LOG_TXT_PATH = "./source/logfiles/workstationLog.txt"
DEVICE_XML_PATH = "./source/logfiles/Device-Copy1.xml"
MAKO_TCW_PATH = "./source/logfiles/makoTest2.tcw"


def changeFile():
    tree = ET.parse(DEVICE_XML_PATH)
    root = tree.getroot()

    print(root.tag)
