from .environmentSetup import *

# Save compiled code to JSON file
with open("./source/compiled_code.json", "r") as file:
    contractInfo = json.load(file)

# Deploy file Prereqs
# Get bytecode
bytecode = contractInfo["contracts"]["DataTracker.sol"]["DataTracker"]["evm"][
    "bytecode"
]["object"]

# get abi and load contract into memory
abi = contractInfo["contracts"]["DataTracker.sol"]["DataTracker"]["abi"]
os.environ["abi"] = json.dumps(abi)
try:
    dtContract = w3.eth.contract(
        address=os.environ["contract_address"], abi=abi
    )  # our contract
except Exception as e:
    print(e)
