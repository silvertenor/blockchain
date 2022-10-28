from loadContract import *


pvsTx = dtContract.functions.retrieve().call()[3]
history = []
while pvsTx:
    tx = w3.eth.get_transaction(pvsTx)
    try:
        obj, params = dtContract.decode_function_input(tx['input'])
        print(params)
        params['_time'] = decrypt(params['_time'])
        params['_userID'] = decrypt(params['_userID'])
        pvsTx = params['_previousTx']
        history.append(params)
    except:
        pvsTx = False     

pvsTx = dtContract.functions.retrieve().call()[3]
history = []
while pvsTx:
    tx = w3.eth.get_transaction(pvsTx)
    try:
        obj, params = dtContract.decode_function_input(tx['input'])
        pvsTx = params['_previousTx']
        history.append(params)
    except:
        pvsTx = False   

print(history)