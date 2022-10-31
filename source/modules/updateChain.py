from dateutil.parser import parse
import hashlib
from .loadContract import *
from cryptography.fernet import Fernet
import pandas as pd

# Constants
LOG_TXT_PATH = "./source/logfiles/workstationLog.txt"
DEVICE_XML_PATH = "./source/logfiles/Device.xml"
MAKO_TCW_PATH = "./source/logfiles/makoTest2.tcw"


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
    store_transaction = dtContract.functions.addConfig(
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
    print("New value of hash: " + dtContract.functions.retrieve().call()[0])


def encrypt(paramToEncrypt):
    # Read the key
    with open("./source/secrets/mykey.key", "rb") as mykey:
        key = mykey.read()
    # Encrypt the value
    f = Fernet(key)
    encryptedParam = f.encrypt(bytes(paramToEncrypt, "utf-8"))
    return encryptedParam


def decrypt(paramToDecrypt):
    # Read the key
    with open("./source/secrets/mykey.key", "rb") as mykey:
        key = mykey.read()

    f = Fernet(key)
    decryptedParam = f.decrypt(bytes(paramToDecrypt, "utf-8")).decode()
    return decryptedParam


def chainChecker():
    # Query the hash stored on the blockchain
    on_chain_hash = dtContract.functions.retrieve().call()[0]
    print("On-chain hash: {}".format(on_chain_hash))
    # Generate the hash of the log file
    device_hash = "0x" + hashGenerator(DEVICE_XML_PATH).hexdigest()
    print("Local hash: {}".format(device_hash))
    # compare the two - if different, update the blockchain!
    if on_chain_hash != device_hash:
        # Gather metadata:
        computer_id, date_changed = fileParser(LOG_TXT_PATH)
        # Get previous tx hash
        previousTxHash = w3.eth.get_block("latest")["transactions"][0].hex()
        # Encrypt the metadata before updating the chain
        computer_id, date_changed = encrypt(computer_id), encrypt(date_changed)
        # Update blockchain
        updateBlockChain(date_changed, device_hash, computer_id, previousTxHash)
    else:
        print("No change detected. Exiting program.")

    # ONLY RUN THIS FOR DEMO PURPOSES
    computer_id, date_changed = fileParser(LOG_TXT_PATH)
    # Encrypt the metadata before updating the chain
    computer_id, date_changed = encrypt(computer_id), encrypt(date_changed)
    blockNum = w3.eth.block_number
    for i in range(blockNum, 0, -1):
        toContract = w3.eth.get_transaction_by_block(i, 0)["to"]
        if toContract == dtContract.address:
            # Get previous tx hash
            previousTxHash = w3.eth.get_block(i)["transactions"][0].hex()

            # Update blockchain
            updateBlockChain(date_changed, device_hash, computer_id, previousTxHash)
            break
