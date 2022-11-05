from .loadContract import *
from .updateChain import decrypt, chainChecker
import pandas as pd
import logging


def getHistory():
    logging.info("Looking for stored contract address...")
    try:
        dtContract = w3.eth.contract(
            address=os.environ["contract_address"], abi=json.loads(os.environ["abi"])
        )
        logging.info("Contract address loaded")
    except:
        logging.error(
            "Could not find contract address. Either update .env or deploy new contract"
        )
    logging.info(
        "Traversing chain from most recent block to find your contract" "s history..."
    )
    try:
        blockNum = w3.eth.block_number
        for i in range(blockNum, 0, -1):
            toContract = w3.eth.get_transaction_by_block(i, 0)["to"]
            if toContract == dtContract.address:
                pvsTx = w3.eth.get_block(i)["transactions"][0].hex()
                # print(previousTxHash)
                break
        print(pvsTx)
        history = []
        while pvsTx:
            tx = w3.eth.get_transaction(pvsTx)
            try:
                obj, params = dtContract.decode_function_input(tx["input"])
                print(params)
                # exit()
                params["_configChanged"] = decrypt(params["_configChanged"])
                params["_userID"] = decrypt(params["_userID"])
                params["_domain"] = decrypt(params["_domain"])
                pvsTx = params["_previousTx"]
                history.append(params)
            except:
                pvsTx = False
        # print(history)
        df = pd.DataFrame(history)
        df = df[["_configChanged", "_userID", "_domain", "_hashNumber", "_previousTx"]]
        df.rename(
            columns={
                "_configChanged": "Date",
                "_userID": "User ID",
                "_domain": "Domain",
                "_hashNumber": "Hash",
                "_previousTx": "Previous Transaction",
            },
            inplace=True,
        )
    except:
        logging.error(
            "Error finding contract"
            "s history. Make sure correct address is stored and that initial contract is deployed."
        )
    # print(df)
    return df
