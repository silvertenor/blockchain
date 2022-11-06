from .updateChain import *
import xml.etree.ElementTree as ET
import random
import re
import logging
import os


def changeFile(basedir):
    try:
        logging.info("Looking for XML file...")
        # Open Device.XML file and read the lines
        DEVICE_XML_PATH = os.path.join(basedir, "source/logfiles", "Device.xml")
        with open(DEVICE_XML_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()
        # Initialize new data to be overwritten
        newFileLines = []
        # Determine which data will change
        logging.info("Changing IP addresses to randomly generated ones...")
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
        with open(DEVICE_XML_PATH, "w", encoding="utf-8") as file:
            file.writelines(newFileLines)
        logging.info("XML file updated with new IPs!")
    except Exception as e:
        logging.error("Error updating XML file. Make sure it is in the right location!")
        logging.error(e)


# Function to update chain once file has been changed
def updateChain(basedir):
    chainChecker(basedir)
