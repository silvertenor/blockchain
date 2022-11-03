from .loadContract import *
from .updateChain import decrypt, chainChecker
import pandas as pd


def getHistory():
    chainChecker()
    pvsTx = dtContract.functions.retrieve().call()[3]
    history = []
    while pvsTx:
        tx = w3.eth.get_transaction(pvsTx)
        try:
            obj, params = dtContract.decode_function_input(tx["input"])
            params["_time"] = decrypt(params["_time"])
            params["_userID"] = decrypt(params["_userID"])
            pvsTx = params["_previousTx"]
            history.append(params)
        except:
            pvsTx = False

    pvsTx = dtContract.functions.retrieve().call()[3]
    history = []
    while pvsTx:
        tx = w3.eth.get_transaction(pvsTx)
        try:
            obj, params = dtContract.decode_function_input(tx["input"])
            params["_time"] = decrypt(params["_time"])
            params["_userID"] = decrypt(params["_userID"])
            pvsTx = params["_previousTx"]
            history.append(params)
        except:
            pvsTx = False
    df = pd.DataFrame(history)
    df = df[["_time", "_userID", "_hashNumber", "_previousTx"]]
    df.rename(
        columns={
            "_time": "Date",
            "_userID": "User ID",
            "_hashNumber": "Hash",
            "_previousTx": "Previous Transaction",
        },
        inplace=True,
    )
    # print(df)
    return df
