from .environmentSetup import *
from .updateChain import decrypt, chainChecker
import pandas as pd
import logging, zlib, base64

basedir = os.environ["basedir"]


def getHistory():
    logging.info("Looking for stored contract address...")
    try:
        dtContract = w3.eth.contract(
            address=os.environ["contract_address"], abi=json.loads(os.environ["abi"])
        )
        logging.info("Contract address loaded")
        logging.info(dtContract.address)
    except:
        logging.error(
            "Could not find contract address. Either update .env or deploy new contract"
        )
    logging.info(
        "Traversing chain from most recent block to find your contract" "s history..."
    )
    blockNumMostRecent = w3.eth.block_number
    try:
        blockNumContractTx = w3.eth.get_transaction(os.environ["contract_tx"])[
            "blockNumber"
        ]
        if blockNumContractTx == blockNumMostRecent:
            searchRange = range(blockNumMostRecent, 0, -1)
        else:
            searchRange = range(blockNumMostRecent, blockNumContractTx, -1)
        for i in searchRange:
            toContract = w3.eth.get_transaction_by_block(i, 0)["to"]
            if toContract == dtContract.address:
                print("--------" * 5)
                print(toContract)
                print(dtContract.address)
                pvsTx = w3.eth.get_block(i)["transactions"][0].hex()
                break
        history = []
        txFlag = False
        while pvsTx:
            if not txFlag:
                tx = w3.eth.get_transaction(pvsTx)
            try:
                obj, params = dtContract.decode_function_input(tx["input"])
                if "_configChanged" in params:
                    txFlag = False
                    params["_configChanged"] = decrypt(params["_configChanged"])
                    params["_userID"] = decrypt(params["_userID"])
                    params["_domain"] = decrypt(params["_domain"])
                    params["_fileDiff"] = zlib.decompress(
                        base64.urlsafe_b64decode(params["_fileDiff"])
                    )
                    pvsTx = params["_previousTx"]
                    history.append(params)
                else:
                    print(pvsTx)
                    print(tx["blockNumber"])
                    txFlag = True
                    tx = w3.eth.get_transaction_by_block(tx["blockNumber"] - 1, 0)

            except:
                pvsTx = False
        df = pd.DataFrame(history)
        df = df[
            [
                "_configChanged",
                "_userID",
                "_domain",
                "_hashNumber",
                "_fileDiff",
                "_previousTx",
            ]
        ]
        df.rename(
            columns={
                "_configChanged": "Date",
                "_userID": "User ID",
                "_domain": "Domain",
                "_hashNumber": "Hash",
                "_fileDiff": "File Diff",
                "_previousTx": "Previous Transaction",
            },
            inplace=True,
        )
        return df
    except Exception as e:
        logging.error(
            "Error finding contract"
            "s history. Make sure correct address is stored and that initial contract is deployed."
        )
        logging.error(e)
