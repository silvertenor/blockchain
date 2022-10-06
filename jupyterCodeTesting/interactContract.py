#!/usr/bin/env python
# coding: utf-8

# # Interaction of Parsed Data, Hashes, and Deployed Contracts
# <hr/>

# ## Set up Environment and Load the Contract from Memory
# Our setup consists of:
# - Importing all required packages
# - Loading the environment variables from ```.env```
# - Setting the paths for GE files
# - Loading the deployed contract into memory

# In[1]:


# web3.../deploy.py
import json
from web3 import Web3
from dotenv import load_dotenv, find_dotenv
import os

# load from .env file
load_dotenv(find_dotenv())

import hashlib

# Constants
LOG_TXT_PATH = 'logfiles/workstationLog.txt'
DEVICE_XML_PATH = 'logfiles/Device.xml'
MAKO_TCW_PATH = 'logfiles/makoTest2.tcw'

# Run module to load contract
get_ipython().run_line_magic('run', './loadContract.ipynb')


# ## Query Blockchain and Log File to Compare Hashes
# The following functions are used to generate the hash of the stored configuration file and comparing it with the hash that is stored on-chain. Here are the steps involved:
# 1. Query the on-chain hash of the specified log file
# 2. Generate the hash of the file that is on our local filesystem
# 3. Compare the two:
#     - If they are the same, no action is taken
#     - If they differ, a new block is appended to the chain with the updated hash and other metadata

# In[2]:


# Read file in chunks (future-proofing) and generate hash:
def hashGenerator(file, buffer_size = 65536):
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
    with open(file, 'rb') as f:
        chunk = f.read(buffer_size)
        # Keep reading and updating hash as long as there is more data:
        while len(chunk) > 0:
            file_hash.update(chunk)
            chunk = f.read(buffer_size)
    return file_hash


# In[3]:


# Function to update blockchain
def updateBlockChain(new_hash):
    """
    This function updates the blockchain by calling the 'store' function of the
    smart contract.

    Parameters
    ----------
    new_hash : type 'str'
        hash of file obtained from hashGenerator function

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
    store_transaction = hash_storage.functions.store(new_hash).build_transaction(
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
    print(
        "New value of hash: " + str(hash_storage.functions.retrieve().call())
    )


# Go through log files:
from dateutil.parser import parse

# Gather pertinent info from log file
computer_name = None
config_pushed = False
config_complete = None
with open(LOG_TXT_PATH, 'r') as file:
    for line in file.readlines():
        # print(line)
        # Extract computer name
        if 'desktop' in line.lower() and '.' not in line:
            computer_name = line.split(' ')[-1]
        if 'starting publish' in line.lower():
            pass# print(line)
        if 'download complete' in line.lower():
            # print(line)
            config_pushed = True
            config_complete = parse(line[:line.index(',')])
if computer_name and config_pushed:          
    print('Computer name: ' + computer_name)
    print('Configuration changed on: ' + str(config_complete))


# Query the hash stored on the blockchain
on_chain_hash = str(hash_storage.functions.retrieve().call())
print('On-chain hash: {}'.format(on_chain_hash))
# Generate the hash of the log file
device_hash = '0x' + hashGenerator(DEVICE_XML_PATH).hexdigest()
print('Local hash: {}'.format(device_hash))
# compare the two - if different, update the blockchain!
if on_chain_hash != device_hash:
    updateBlockChain(device_hash)
else:
    print('No change detected. Exiting program.')

