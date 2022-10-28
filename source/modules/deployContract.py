from environmentSetup import *
# Time the notebook
import datetime
start = datetime.datetime.now()

# web3.../deploy.py
from solcx import compile_standard, install_solc

# Install solc compiler
install_solc("0.6.0")

def compileSolFile():
    with open("./source/DataTracker.sol", "r") as file:
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
    with open("./source/compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

    # Deploy file Prereqs
    # Get bytecode
    bytecode = compiled_sol["contracts"]["DataTracker.sol"]["DataTracker"]["evm"]["bytecode"]["object"]

    # get abi
    abi = compiled_sol["contracts"]["DataTracker.sol"]["DataTracker"]["abi"]

    return bytecode, abi

def deployContract(bytecode, abi):
    # Now we have all parameters we need to interact with Ganache local chain
    dtContract = w3.eth.contract(abi=abi, bytecode=bytecode)  # This is our contract
    # Get latest transaction:
    nonce = w3.eth.getTransactionCount(
        my_address
    )  # gives our nonce - number of transactions
    # print(nonce)
    # 1. Build a transacton
    # 2. Sign a transaction
    # 3. Send a transaction
    transaction = dtContract.constructor().buildTransaction(
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

    return contract_address

def updateEnv(contract_address):
    file_lines = []
    with open('./.env', 'r') as file:
        for line in file:
            if 'contract_address' not in line.lower():
                if '\n' not in line:
                    line += '\n'
                file_lines.append(line)
    with open('./.env', 'w') as file:
        for line in file_lines:
            file.writelines(line)
        file.writelines('contract_address=' + contract_address)


# Entry point
bytecode, abi = compileSolFile()
contractAdd = deployContract(bytecode, abi)
updateEnv(contractAdd)

end = datetime.datetime.now()
print('Total execution time: {}'.format(str(end-start)))