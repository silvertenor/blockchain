# web3.../deploy.py
import json
from web3 import Web3
from dotenv import load_dotenv, find_dotenv
import os
from dateutil.parser import parse
from cryptography.fernet import Fernet

# load from .env file
load_dotenv(find_dotenv())

import hashlib

# Constants
LOG_TXT_PATH = "logfiles/workstationLog.txt"
DEVICE_XML_PATH = "logfiles/Device.xml"
MAKO_TCW_PATH = "logfiles/makoTest2.tcw"


# Save compiled code to JSON file
with open("./compiled_code.json", "r") as file:
    contractInfo = json.load(file)

# Deploy file Prereqs
# Get bytecode
bytecode = contractInfo["contracts"]["HashStorage.sol"]["HashStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = contractInfo["contracts"]["HashStorage.sol"]["HashStorage"]["abi"]
w3 = Web3(
    Web3.HTTPProvider("HTTP://127.0.0.1:7545")
)  # Get this address from RPC provider in ganache GUI
chain_id = 1337  # From Network ID of ganache GUI
my_address = os.getenv(
    "PUBLIC_KEY"
)  # address to deploy from - one of fake accounts in GUI
private_key = os.getenv("PRIVATE_KEY")  # From key symbol next to account
contract_address = os.getenv("contract_address")  # our contract's address
hash_storage = w3.eth.contract(address=contract_address, abi=abi)  # our contract


def fileParser(file):
    # Gather pertinent info from log file
    computer_name = None
    config_pushed = False
    config_complete = None
    with open(file, "r") as file:
        for line in file.readlines():
            # print(line)
            # Extract computer name
            if "desktop" in line.lower() and "." not in line:
                computer_name = line.split(" ")[-1][:-1]
            if "starting publish" in line.lower():
                pass  # print(line)
            if "download complete" in line.lower():
                # print(line)
                config_pushed = True
                config_complete = parse(line[: line.index(",")])
    if computer_name and config_pushed:
        # print('Computer name: ' + computer_name)
        # print('Configuration changed on: ' + str(config_complete))
        return computer_name, str(config_complete)


# Read file in chunks (future-proofing) and generate hash:
def hashGenerator(file, buffer_size=65536):
    """
    This function reads a given file in chunks and generates a corresponding
    SHA256 hash.

    Parameters
    ----------
    file : type 'str'
        relative path to file to hash
    buffer_size : {65536, 'other'}, optional
        number of bytes to read, by default 65536

    Returns
    -------
    file_hash
        the SHA256 hash of the file provided

    Raises
    ------
    N/A
    """
    file_hash = hashlib.sha256()
    # Read file as binary
    with open(file, "rb") as f:
        chunk = f.read(buffer_size)
        # Keep reading and updating hash as long as there is more data:
        while len(chunk) > 0:
            file_hash.update(chunk)
            chunk = f.read(buffer_size)
    return file_hash


# Function to update blockchain
def updateBlockChain(date, new_hash, computer_id, pvsTx):
    """
    This function updates the blockchain by calling the 'store' function of the
    smart contract.

    Parameters
    ----------
    new_hash : type 'str'
        hash of file obtained from hashGenerator function
    date : type 'str'
        date the configuration was changed
    computer_id : type 'str'
        ID of the computer/user. Found in the top line of the log file
    Returns
    -------
    None

    Raises
    ------
    N/A
    """
    print("Updating contract...")

    # Get latest transaction:
    nonce = w3.eth.getTransactionCount(
        my_address
    )  # gives our nonce - number of transactions
    # Store new value for hashNumber:
    store_transaction = hash_storage.functions.addHash(
        date, new_hash, computer_id, pvsTx
    ).build_transaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
        }
    )
    signed_store_tx = w3.eth.account.sign_transaction(
        store_transaction, private_key=private_key
    )
    send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
    print("Updated!")
    print("New value of hash: " + hash_storage.functions.retrieve().call()[0])


def encrypt(paramToEncrypt):
    # Read the key
    with open("mykey.key", "rb") as mykey:
        key = mykey.read()
    # Encrypt the value
    f = Fernet(key)
    encryptedParam = f.encrypt(bytes(paramToEncrypt, "utf-8"))
    return encryptedParam


def decrypt(paramToDecrypt):
    # Read the key
    with open("mykey.key", "rb") as mykey:
        key = mykey.read()

    f = Fernet(key)
    decryptedParam = f.decrypt(bytes(paramToDecrypt, "utf-8")).decode()
    return decryptedParam
