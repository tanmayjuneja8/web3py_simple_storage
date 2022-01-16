from eth_keys.datatypes import PrivateKey
from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compile
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]},
            },
        },
    },
    solc_version="0.6.0",
)
with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

# bytecode

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to ganache
w3 = Web3(
    Web3.HTTPProvider("https://kovan.infura.io/v3/561d47168f73460180fc05c3a338b6d7")
)
chainid = 42
my_address = "0xb13d0B3183dD094Dd6f5e711D56f7F11cc1f8ba5"
pvt_key = os.getenv("PRIVATE_KEY")

# create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# latest transaction
nonce = w3.eth.getTransactionCount(my_address)
"""
1. Build a Transaction.
2. Sign a Transaction.
3. Send a Transaction. 
"""
# 1. Build a txn
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chainid,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
# 2. Sign a txn
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=pvt_key)

# 3. Send a txn
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_reciept = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
""" 
For working with the contracts,
We need two things
 1. Contract address
 2. Contract ABI
"""
simple_storage = w3.eth.contract(address=tx_reciept.contractAddress, abi=abi)
"""
while transacting with the blockchain, there are exactly 2 ways in which we can interact:-

1. call(Blue button) -> makes a call and gets a return value. Does not make a state change to the blockchain.
2. Transact(Orange Button) -> makes a state change in the blockchain.

"""

# intial value of favorite number
print(simple_storage.functions.retrieve().call())
store_txn = simple_storage.functions.store(69).buildTransaction(
    {
        "chainId": chainid,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

signed_store_tx = w3.eth.account.sign_transaction(store_txn, private_key=pvt_key)

print("Updating contract...")
trans_hash = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(trans_hash)
print("Updated!")
print(simple_storage.functions.retrieve().call())
