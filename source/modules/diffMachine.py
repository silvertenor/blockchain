import diff_match_patch as dmpModule
from .environmentSetup import *
from .environmentUpdate import *
from .updateChain import decrypt
import logging, zlib, base64


def diffDisplay():
    logging.info("Looking for stored contract address...")
    try:
        dtContract = w3.eth.contract(
            address=os.environ["contract_address"], abi=json.loads(os.environ["abi"])
        )
        print("CONTRACT ADDRESS" + os.environ["contract_address"])
        logging.info("Contract address loaded")
    except:
        logging.error(
            "Could not find contract address. Either update .env or deploy new contract"
        )
    logging.info(
        "Traversing chain from most recent block to find your contract" "s history..."
    )
    blockNumMostRecent = w3.eth.block_number
    try:
        blockNumLastTx = w3.eth.get_transaction(os.environ["last_tx"])["blockNumber"]
        if blockNumLastTx == blockNumMostRecent:
            pvsTx = w3.eth.get_block(blockNumMostRecent)["transactions"][0].hex()
        else:
            for i in range(blockNumMostRecent, blockNumLastTx, -1):
                toContract = w3.eth.get_transaction_by_block(i, 0)["to"]
                if toContract == dtContract.address:
                    pvsTx = w3.eth.get_block(i)["transactions"][0].hex()
                    break
        diffs = []
        times = []
        names = []
        while pvsTx:
            tx = w3.eth.get_transaction(pvsTx)
            if tx != w3.eth.get_transaction(os.environ["file_tx"]):
                obj, params = dtContract.decode_function_input(tx["input"])
                params["_fileDiff"] = zlib.decompress(
                    base64.urlsafe_b64decode(params["_fileDiff"])
                )
                params["_configChanged"] = decrypt(params["_configChanged"])
                pvsTx = params["_previousTx"]
                diffs.append(params["_fileDiff"])
                names.append(decrypt(params["_userID"]))
                times.append(params["_configChanged"])
            else:
                pvsTx = False
    except:
        pass
    tx = w3.eth.get_transaction(os.environ["file_tx"])

    try:
        obj, params = dtContract.decode_function_input(tx["input"])
        old = zlib.decompress(base64.urlsafe_b64decode(params["_fileDiff"])).decode(
            encoding="utf-8"
        )
    except Exception as e:
        logging.error(e + "In source.modules.updateChain.fileDiff()")
        pass
    dmp = dmpModule.diff_match_patch()
    i = 1
    displayDiffs = []
    for diff in diffs:
        hist = dmp.patch_apply(dmp.patch_fromText(diff.decode()), old)[0]
        i += 1
        differences = dmp.diff_main(old, hist)
        dmp.diff_cleanupEfficiency(differences)
        displayDiffs.append(dmp.diff_prettyHtml(differences))
    labels = [i + " - " + j for i, j in zip(times, names)]
    print(times)
    return displayDiffs, labels
