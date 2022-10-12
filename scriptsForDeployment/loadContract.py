#!/usr/bin/env python
# coding: utf-8

# # Loading our Deployed Contract Into Memory
# <hr/>

# ## Load Contract Info from JSON File

# In[ ]:


# Save compiled code to JSON file
with open("compiled_code.json", "r") as file:
    contractInfo = json.load(file)
    
# Deploy file Prereqs
# Get bytecode
bytecode = contractInfo["contracts"]["HashStorage.sol"]["HashStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = contractInfo["contracts"]["HashStorage.sol"]["HashStorage"]["abi"]


# ## Set up Blockchain Connection and Load Contract

# In[ ]:


w3 = Web3(
    Web3.HTTPProvider("HTTP://127.0.0.1:7545")
)  # Get this address from RPC provider in ganache GUI
chain_id = 1337  # From Network ID of ganache GUI
my_address = os.getenv("PUBLIC_KEY")  # address to deploy from - one of fake accounts in GUI
private_key = os.getenv("PRIVATE_KEY")  # From key symbol next to account
contract_address = os.getenv("contract_address") # our contract's address
hash_storage = w3.eth.contract(address=contract_address, abi=abi) # our contract

