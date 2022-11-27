from .environmentSetup import *
import pandas as pd


def query():
    dtContract = w3.eth.contract(
        address=os.environ["contract_address"], abi=json.loads(os.environ["abi"])
    )
    admins = dtContract.functions.viewAdmins().call()
    users = dtContract.functions.viewUsers().call()
    df = pd.DataFrame(columns=["Account", "Role"])
    for item in admins:
        df = df.append({"Account": item, "Role": "Admin"}, ignore_index=True)
    for item in users:
        df = df.append({"Account": item, "Role": "User"}, ignore_index=True)
    return df


def add(name, user, role):
    dtContract = w3.eth.contract(
        address=os.environ["contract_address"], abi=json.loads(os.environ["abi"])
    )
    nonce = w3.eth.getTransactionCount(
        os.environ["my_address"]
    )  # gives our nonce - number of transactions
    # Store new value for hashNumber:
    if role == "Admin":
        store_transaction = dtContract.functions.addAdmin(user).build_transaction(
            {
                "gasPrice": w3.eth.gas_price,
                "chainId": chain_id,
                "from": os.environ["my_address"],
                "nonce": nonce,
            }
        )
    if role == "User":
        store_transaction = dtContract.functions.addUser(user).build_transaction(
            {
                "gasPrice": w3.eth.gas_price,
                "chainId": chain_id,
                "from": os.environ["my_address"],
                "nonce": nonce,
            }
        )
    # Sign transaction
    signed_store_tx = w3.eth.account.sign_transaction(
        store_transaction, private_key=private_key
    )
    # Send transaction
    send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
    # Wait for receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
    print(tx_receipt)
