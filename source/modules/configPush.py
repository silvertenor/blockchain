from .updateChain import *
import xml.etree.ElementTree as ET
import random
import re

LOG_TXT_PATH = "./source/logfiles/workstationLog.txt"
DEVICE_XML_PATH = "./source/logfiles/Device.xml"
MAKO_TCW_PATH = "./source/logfiles/makoTest2.tcw"


def changeFile():
    # Open Device.XML file and read the lines
    with open(DEVICE_XML_PATH, "r") as file:
        lines = file.readlines()
    # Initialize new data to be overwritten
    newFileLines = []
    # Determine which data will change
    for line in lines:
        if "IPAddress" in line:
            # Create new IP address (randomly generated)
            newIp = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
            currentIp = re.findall(r"[0-9]+(?:\.[0-9]+){3}", line)
            for ip in currentIp:
                line = line.replace(ip, newIp)
        # Add each line (even changed ones) to data to be written to file
        newFileLines.append(line)
    # Write our new garbage values to file
    with open(DEVICE_XML_PATH, "w") as file:
        file.writelines(newFileLines)


# Function to update chain once file has been changed
def updateChain():
    chainChecker()
