from web3 import Web3
from dotenv import load_dotenv, find_dotenv, set_key
import os
import json
import logging

logging.info("Looking for .env file to load in variables...")
try:
    load_dotenv(find_dotenv())
    project_root = os.getenv("PROJECT_ROOT")  # To change in next step
    os.chdir(project_root)
    # load secrets
    os.environ["my_address"] = os.getenv(
        "PUBLIC_KEY"
    )  # address to deploy from - one of fake accounts in GUI
    private_key = os.getenv("PRIVATE_KEY")  # From key symbol next to account
    w3 = Web3(
        Web3.HTTPProvider(os.getenv("WEB3_PROVIDER"))
    )  # Get this address from RPC provider in ganache GUI
    chain_id = int(os.getenv("CHAIN_ID"))  # From Network ID of ganache GUI
    try:
        os.environ["contract_address"] = os.getenv(
            "CONTRACT_ADDRESS"
        )  # our contract's address
        buttonsAllowed = True
    # Change to proper working directory
    except:
        buttonsAllowed = False

except Exception as e:
    logging.error(
        "Could not find certain environment variables. Please make sure .env is up to date."
    )
    # logging.error('Error')
