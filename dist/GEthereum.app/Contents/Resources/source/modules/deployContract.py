from .environmentSetup import *
from .updateChain import *
from .history import *
import os

# Time the notebook
import datetime

start = datetime.datetime.now()

# web3.../deploy.py
from solcx import compile_standard, install_solc

# Install solc compiler
install_solc("0.6.0")

basedir = os.environ["basedir"]


def compileSolFile():
    with open(os.path.join(basedir, "source", "DataTracker.sol"), "r") as file:
        dt_file = file.read()

    # Compile our solidity

    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"DataTracker.sol": {"content": dt_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.6.0",
    )

    # Save compiled code to JSON file
    with open(os.path.join(basedir, "source", "compiled_code.json"), "w") as file:
        json.dump(compiled_sol, file)

    # Deploy file Prereqs
    # Get bytecode
    bytecode = compiled_sol["contracts"]["DataTracker.sol"]["DataTracker"]["evm"][
        "bytecode"
    ]["object"]

    # get abi
    abi = compiled_sol["contracts"]["DataTracker.sol"]["DataTracker"]["abi"]
    os.environ["abi"] = json.dumps(abi)

    return bytecode, abi


def deployContract(bytecode, abi):
    # Now we have all parameters we need to interact with Ganache local chain
    dtContract = w3.eth.contract(abi=abi, bytecode=bytecode)  # This is our contract
    # Get latest transaction:
    nonce = w3.eth.getTransactionCount(
        os.environ["my_address"]
    )  # gives our nonce - number of transactions
    # print(nonce)
    # 1. Build a transacton
    # 2. Sign a transaction
    # 3. Send a transaction
    transaction = dtContract.constructor().buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": chain_id,
            "from": os.environ["my_address"],
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
    os.environ["contract_address"] = tx_receipt.contractAddress
    print("Deployed!")

    return os.environ["contract_address"]


def updateEnv(contract_address):
    file_lines = []
    set_key(
        os.path.join(basedir, "source", ".env"), "CONTRACT_ADDRESS", contract_address
    )


# Entry point
def main():
    print("In main")
    bytecode, abi = compileSolFile()
    contractAdd = deployContract(bytecode, abi)
    updateEnv(contractAdd)
    chainChecker()


end = datetime.datetime.now()
print("Total execution time: {}".format(str(end - start)))
