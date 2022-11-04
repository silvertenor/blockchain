from web3 import Web3
from dotenv import load_dotenv, find_dotenv, set_key
import os
import json

load_dotenv(find_dotenv())

# load secrets
os.environ["my_address"] = os.getenv(
    "PUBLIC_KEY"
)  # address to deploy from - one of fake accounts in GUI
private_key = os.getenv("PRIVATE_KEY")  # From key symbol next to account
project_root = os.getenv("PROJECT_ROOT")  # To change in next step
w3 = Web3(
    Web3.HTTPProvider(os.getenv("WEB3_PROVIDER"))
)  # Get this address from RPC provider in ganache GUI
chain_id = int(os.getenv("CHAIN_ID"))  # From Network ID of ganache GUI
os.environ["contract_address"] = os.getenv("CONTRACT_ADDRESS")  # our contract's address
# Change to proper working directory
os.chdir(project_root)
