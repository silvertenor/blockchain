from dateutil.parser import parse
import hashlib, zlib, base64

from .environmentSetup import *
from .environmentUpdate import *
from cryptography.fernet import Fernet
import os, socket
from datetime import datetime
import diff_match_patch as dmpModule

basedir = os.environ["basedir"]
# Read the file to upload to chain
def fileRead(file):
    with open(file, "rb") as file:
        contents = file.read()
    return contents


# Get diff of file
def fileDiff(file, pvsFile):
    dmp = dmpModule.diff_match_patch()
    with open(file, "r") as file:
        new = file.read()
    with open(pvsFile, "r") as file:
        old = file.read()

    patch = dmp.patch_make(new, old)
    diff = dmp.patch_toText(patch)
    patches = dmp.patch_fromText(diff)
    new_text, _ = dmp.patch_apply(patches, new)
    print(new_text)


# Read file in chunks (future-proofing) and generate hash:
def hashGenerator(file, buffer_size=65536):
    """
    This function reads a given file in chunks and generates a corresponding
    SHA256 hash.

    Parameters
    ----------
    file : type 'str'
        relative path to file to hash
    buffer_size : {65536, 'other'}, optional
        number of bytes to read, by default 65536

    Returns
    -------
    file_hash
        the SHA256 hash of the file provided

    Raises
    ------
    N/A
    """
    file_hash = hashlib.sha256()
    # Read file as binary
    with open(file, "rb") as f:
        chunk = f.read(buffer_size)
        # Keep reading and updating hash as long as there is more data:
        while len(chunk) > 0:
            file_hash.update(chunk)
            chunk = f.read(buffer_size)
    return file_hash


# Function to update blockchain
def updateBlockChain(contract, *args):
    """
    This function updates the blockchain by calling the 'store' function of the
    smart contract.

    Parameters
    ----------
    *args - a tuple of arguments to be inserted into struct stored on chain
    Returns
    -------
    None

    Raises
    ------
    N/A
    """
    # print("Updating contract...")

    # Get latest transaction:
    nonce = w3.eth.getTransactionCount(
        os.environ["my_address"]
    )  # gives our nonce - number of transactions
    # Store new value for hashNumber:

    store_transaction = contract.functions.addConfig(*args).build_transaction(
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
    # print("TX RECEIPT")
    return tx_receipt["transactionHash"].hex()
    # print("Updated!")
    # print("New value of hash: " + dtContract.functions.retrieve().call()[0])


def encrypt(paramToEncrypt):
    """
    This function uses a stored secret key to encrypt a string and return it
    to the calling function so values can be safely added to the chain.

    Parameters
    ----------
    paramToEncrypt : type 'str'
        parameter to encrypt

    Returns
    -------
    encryptedParam
        the encrypted parameter

    Raises
    ------
    N/A
    """
    # Read the key
    keyPath = os.path.join(basedir, "source/secrets", "mykey.key")
    with open(keyPath, "rb") as mykey:
        key = mykey.read()
    # Encrypt the value
    f = Fernet(key)
    encryptedParam = f.encrypt(bytes(paramToEncrypt, "utf-8"))
    return encryptedParam


def decrypt(paramToDecrypt):
    """
    This function uses a stored secret key to decrypt a string and return it
    to the calling function so values can be read into the GUI.

    Parameters
    ----------
    paramToDecrypt : type 'str'
        parameter to decrypt

    Returns
    -------
    encryptedParam
        the encrypted parameter

    Raises
    ------
    N/A
    """
    # Read the key
    keyPath = os.path.join(basedir, "source/secrets", "mykey.key")
    with open(keyPath, "rb") as mykey:
        key = mykey.read()

    f = Fernet(key)
    decryptedParam = f.decrypt(bytes(paramToDecrypt, "utf-8")).decode()
    return decryptedParam


def chainChecker(
    DEVICE_XML_PATH=os.path.join(basedir, "source/logfiles", "Device.xml")
):
    """
    This function checks the on-chain hash of the Device.xml file and compares it
    to what is on the local filesystem. If they are different, a change has been
    made and the blockchain should be updated. If they are the same, nothing will
    happen.

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    N/A
    """
    # Query the hash stored on the blockchain
    dtContract = w3.eth.contract(
        address=os.environ["contract_address"], abi=json.loads(os.environ["abi"])
    )
    print("loaded addr: " + dtContract.address)
    on_chain_hash = dtContract.functions.retrieve().call()[0]
    print("On-chain hash: {}".format(on_chain_hash))
    # Generate the hash of the log file
    device_hash = "0x" + hashGenerator(DEVICE_XML_PATH).hexdigest()
    print("Local hash: {}".format(device_hash))
    # compare the two - if different, update the blockchain!
    if on_chain_hash != device_hash:
        # print("DIFFERENCE DETECTED")
        # Gather metadata:
        user, domain, date_changed = (
            os.environ.get("USER"),  # logged in user
            socket.gethostname(),  # Domain of user
            str(
                datetime.fromtimestamp(os.path.getmtime(DEVICE_XML_PATH)).replace(
                    microsecond=0
                )
            ),
        )
        # Encrypt the metadata before updating the chain
        user, domain, date_changed = (
            encrypt(user),
            encrypt(domain),
            encrypt(date_changed),
        )
        # Update blockchain
        blockNumMostRecent = w3.eth.block_number
        try:
            blockNumLastTx = w3.eth.get_transaction(os.environ["last_tx"])[
                "blockNumber"
            ]
            print(blockNumLastTx)
        except:
            pass
        if blockNumLastTx and (blockNumLastTx != blockNumMostRecent):
            for i in range(blockNumMostRecent, blockNumLastTx, -1):
                toContract = w3.eth.get_transaction_by_block(i, 0)["to"]
                # If our contract already has been modified
                if toContract == dtContract.address:
                    # Get previous tx hash
                    previousTxHash = w3.eth.get_block(i)["transactions"][0].hex()
                    # print(previousTxHash)
                    print("Updating Chain")
                    fileStuff = base64.urlsafe_b64encode(
                        zlib.compress(fileRead(DEVICE_XML_PATH), 9)
                    )
                    # Update blockchain
                    tx = updateBlockChain(
                        dtContract,
                        date_changed,
                        device_hash,
                        fileStuff,
                        user,
                        domain,
                        previousTxHash,
                    )
                    txDict = {"Last Tx": tx}
                    updateEnv(txDict)
                    os.environ["last_tx"] = tx
                    print("Updated")
                    break
        else:  # If our contract is brand new
            # Random Tx value to not break program
            previousTxHash = w3.eth.get_block("latest")["transactions"][0].hex()
            print("Updating Chain")
            fileStuff = base64.urlsafe_b64encode(
                zlib.compress(fileRead(DEVICE_XML_PATH), 9)
            )
            print(fileStuff)
            tx = updateBlockChain(
                dtContract,
                date_changed,
                device_hash,
                fileStuff,
                user,
                domain,
                previousTxHash,
            )
            txDict = {"Last Tx": tx}
            updateEnv(txDict)
            os.environ["last_tx"] = tx
            print("Updated")
    # else:
    #     # print("No change detected. Exiting program.")
