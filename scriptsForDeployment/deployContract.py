#!/usr/bin/env python
# coding: utf-8

# # Building and Deploying a Smart Contract
# <hr/>

# ### Step 1 - Build the Smart Contract

# In[ ]:


# web3.../deploy.py
from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os

# load from .env file
load_dotenv()

# Install solc compiler
install_solc("0.6.0")

with open("./HashStorage.sol", "r") as file:
    hash_storage_file = file.read()

# Compile our solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"HashStorage.sol": {"content": hash_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

# Save compiled code to JSON file
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Deploy file Prereqs
# Get bytecode
bytecode = compiled_sol["contracts"]["HashStorage.sol"]["HashStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = compiled_sol["contracts"]["HashStorage.sol"]["HashStorage"]["abi"]


# ### Step 2 - Set up Blockchain Connection

# In[ ]:


w3 = Web3(
    Web3.HTTPProvider("HTTP://127.0.0.1:7545")
)  # Get this address from RPC provider in ganache GUI
chain_id = 1337  # From Network ID of ganache GUI
my_address = os.getenv("PUBLIC_KEY")  # address to deploy from - one of fake accounts in GUI
private_key = os.getenv("PRIVATE_KEY")  # From key symbol next to account
# print(private_key)
### BETTER - use os.getenv("PRIVATE_KEY") where private key is stored as environment variable. Can also store in .env file


# ### Step 3 - Deploy Smart Contract

# In[ ]:


# Now we have all parameters we need to interact with Ganache local chain
HashStorage = w3.eth.contract(abi=abi, bytecode=bytecode)  # This is our contract
# Get latest transaction:
nonce = w3.eth.getTransactionCount(
    my_address
)  # gives our nonce - number of transactions
# print(nonce)
# 1. Build a transacton
# 2. Sign a transaction
# 3. Send a transaction
transaction = HashStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# send this signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(
    signed_txn.rawTransaction
)  # Can now view this in 'transactions' in ganache
# Wait for block confirmation:
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# Get address of smart contract:
contract_address = tx_receipt.contractAddress
print("Deployed!")


# ### Step 4 - Update .env File with New Contract Address

# In[ ]:


file_lines = []
with open('.env', 'r') as file:
    for line in file:
        if 'contract_address' not in line.lower():
            file_lines.append(line)
with open('.env', 'w') as file:
    for line in file_lines:
        file.write(line)
    file.write('contract_address=' + contract_address)

