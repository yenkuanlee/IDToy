import datetime
import hashlib
import io
import ipfsapi
import json
import os
import requests
from web3 import Web3, HTTPProvider, TestRPCProvider
from web3.middleware import geth_poa_middleware
from ethereum.abi import (
    decode_abi,
    normalize_name as normalize_abi_method_name,
    method_id as get_abi_method_id)
from ethereum.utils import encode_int, zpad, decode_hex

IPFS_IP = '127.0.0.1'
IPFS_PORT = '5001'
Cpath = os.path.dirname(os.path.realpath(__file__))

class IDToyFramework:
    def __init__(self):
        self.api = ipfsapi.connect(IPFS_IP,IPFS_PORT)
        self.w3 = Web3(HTTPProvider('http://localhost:3000'))
        self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        ### Element contract
        f = open(Cpath+'/contract/contract.json','r')
        Jline = json.loads(f.readline())
        f.close()
        self.abi = Jline['abi']
        contract_address = Jline['contract_address']
        self.contract_instance = self.w3.eth.contract(abi=self.abi, address=contract_address)
        self.NameHash = self.api.object_put(io.BytesIO(json.dumps({"Data":"Name"}).encode()))['Hash']
        self.CountryHash = self.api.object_put(io.BytesIO(json.dumps({"Data":"Country"}).encode()))['Hash']
        self.DescriptionHash = self.api.object_put(io.BytesIO(json.dumps({"Data":"Description"}).encode()))['Hash']
        self.UTCHash = self.api.object_put(io.BytesIO(json.dumps({"Data":"UTC"}).encode()))['Hash']

    #def Register(self,account,publickey,objectkey,email):
    def Register(self,email,passwd,UTC,name,description,country):
        m = hashlib.md5()
        m.update(passwd.encode('utf-8')+email.encode('utf-8'))
        account = m.hexdigest()
        publickey = json.loads(UTC)['address']
        Obyte = json.dumps({"Data":email}).encode()
        objectkey = self.api.object_put(io.BytesIO(Obyte))['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,name,self.NameHash)['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,country,self.CountryHash)['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,description,self.DescriptionHash)['Hash']
        account = self.w3.toBytes(text=account)
        publickey = self.w3.toChecksumAddress(publickey)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)

        unicorn_txn = self.contract_instance.functions.register(account,publickey,objectkey,email).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def GetUserInfo(self,email,passwd):
        m = hashlib.md5()
        m.update(passwd.encode('utf-8')+email.encode('utf-8'))
        account = m.hexdigest()
        account = self.w3.toBytes(text=account)
        result = self.contract_instance.functions.GetUserInfo(account).call()
        return result
