#!/usr/bin/env python
# coding: utf-8

# # Interaction of Parsed Data, Hashes, and Deployed Contracts
# <hr/>

# ### Step 1 - Build the Smart Contract

# In[1]:


# web3.../deploy.py
import json
from web3 import Web3
from dotenv import load_dotenv
import os

# load from .env file
load_dotenv()


# In[2]:


# Save compiled code to JSON file
with open("compiled_code.json", "r") as file:
    contractInfo = json.load(file)
    
# Deploy file Prereqs
# Get bytecode
bytecode = contractInfo["contracts"]["HashStorage.sol"]["HashStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = contractInfo["contracts"]["HashStorage.sol"]["HashStorage"]["abi"]


# ### Step 2 - Set up Blockchain Connection

# In[3]:


w3 = Web3(
    Web3.HTTPProvider("HTTP://127.0.0.1:7545")
)  # Get this address from RPC provider in ganache GUI
chain_id = 1337  # From Network ID of ganache GUI
my_address = os.getenv("PUBLIC_KEY")  # address to deploy from - one of fake accounts in GUI
private_key = os.getenv("PRIVATE_KEY")  # From key symbol next to account
# print(private_key)
### BETTER - use os.getenv("PRIVATE_KEY") where private key is stored as environment variable. Can also store in .env file


# ### Step 3 - Deploy Smart Contract

# In[4]:


# Now we have all parameters we need to interact with Ganache local chain
# Get latest transaction:
nonce = w3.eth.getTransactionCount(
    my_address
)  # gives our nonce - number of transactions


# ### Step 4 - Interact with Smart Contract

# In[5]:


# How do we interact and work with the contract?
# Need
# 1. Contract address
# 2. Contract ABI
contract_address = os.getenv("contract_address")
hash_storage = w3.eth.contract(address=contract_address, abi=abi)
# Now we can interact with our contract with a call or a transact
# Call -> simulate making the call and getting the return value (no state change to blockchain)
# Transact -> actually make a state change (have to build & send transaction)

# initial value of hashNumber:
print(
    "Current value of favorite number: "
    + str(hash_storage.functions.retrieve().call())
)  # No state change!

print("Updating contract...")
# Store new value for hashNumber:
store_transaction = hash_storage.functions.store("0x12332fea").build_transaction(
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
    "New value of favorite number: " + str(hash_storage.functions.retrieve().call())
)


# In[ ]:




