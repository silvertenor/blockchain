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
    simple_storage_file = file.read()

# Compile our solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
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
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to ganache local blockchain
w3 = Web3(
    Web3.HTTPProvider("HTTP://127.0.0.1:7545")
)  # Get this address from RPC provider in ganache GUI
chain_id = 1337  # From Network ID of ganache GUI
my_address = "0x68221dBa30f77Aa23A55c5C583D15408deb76495"  # address to deploy from - one of fake accounts in GUI
private_key = os.getenv("PRIVATE_KEY")  # From key symbol next to account
# print(private_key)
### BETTER - use os.getenv("PRIVATE_KEY") where private key is stored as environment variable. Can also store in .env file

# Now we have all parameters we need to interact with Ganache local chain
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)  # This is our contract
# Get latest transaction:
nonce = w3.eth.getTransactionCount(
    my_address
)  # gives our nonce - number of transactions
# print(nonce)
# 1. Build a transacton
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
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
print("Deployed!")

# How do we interact and work with the contract?
# Need
# 1. Contract address
# 2. Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Now we can interact with our contract with a call or a transact
# Call -> simulate making the call and getting the return value (no state change to blockchain)
# Transact -> actually make a state change (have to build & send transaction)

# initial value of favorite_number
print(
    "Current value of favorite number: "
    + str(simple_storage.functions.retrieve().call())
)  # No state change!

print("Updating contract...")
# Store new value:
store_transaction = simple_storage.functions.store(15).build_transaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_store_tx = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
print(
    "New value of favorite number: " + str(simple_storage.functions.retrieve().call())
)
