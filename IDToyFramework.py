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

    def EmailInUsed(self,email):
        return self.contract_instance.functions.EmailInUsed(email).call()
    def AddressInUsed(self,address):
        return self.contract_instance.functions.AddressInUsed(address).call()
    def GetAccount(self,email,passwd):
        m = hashlib.md5()
        m.update(passwd.encode('utf-8')+email.encode('utf-8'))
        account = m.hexdigest()
        account = self.w3.toBytes(text=account)
        return account

    #def Register(self,account,publickey,objectkey,email):
    def Register(self,email,passwd,UTC,name,description,country):
        if self.EmailInUsed(email):
            return json.dumps({"status":"EmailInUsedException"})
        publickey = json.loads(UTC)['address']
        publickey = self.w3.toChecksumAddress(publickey)
        if self.AddressInUsed(publickey):
            return json.dumps({"status":"AddressInUsedException"})
        Obyte = json.dumps({"Data":email}).encode()
        objectkey = self.api.object_put(io.BytesIO(Obyte))['Hash']
        NameKey = self.api.object_put(io.BytesIO(json.dumps({"Data":name}).encode()))['Hash']
        CountryKey = self.api.object_put(io.BytesIO(json.dumps({"Data":country}).encode()))['Hash']
        DescriptionKey = self.api.object_put(io.BytesIO(json.dumps({"Data":description}).encode()))['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,'Name',NameKey)['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,'Country',CountryKey)['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,'Description',DescriptionKey)['Hash']
        account = self.GetAccount(email,passwd)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)

        unicorn_txn = self.contract_instance.functions.register(account,publickey,objectkey,email).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def GetUserInfo(self,email,passwd):
        if not self.EmailInUsed(email):
            return json.dumps({"status":"EmailNotExistedException"})
        account = self.GetAccount(email,passwd)
        objectkey = self.contract_instance.functions.GetUserInfo(account).call()
        results = self.api.object_get(objectkey)['Links']
        Odict = dict()
        for x in results:
            if x['Name'] == 'Name':
                Odict['Name'] = self.api.object_get(x['Hash'])['Data']
            elif x['Name'] == 'Country':
                Odict['Country'] = self.api.object_get(x['Hash'])['Data']
            elif x['Name'] == 'Description':
                Odict['Description'] = self.api.object_get(x['Hash'])['Data']
        return json.dumps(Odict)

    def SetUserInfo(self,email,passwd,UTC,target,value):
        account = self.GetAccount(email,passwd)
        ValueKey = NameKey = self.api.object_put(io.BytesIO(json.dumps({"Data":value}).encode()))['Hash']
        objectkey = self.contract_instance.functions.GetUserInfo(account).call()
        objectkey = self.api.object_patch_rm_link(objectkey,target)['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,target,ValueKey)['Hash']

        publickey = json.loads(UTC)['address']
        publickey = self.w3.toChecksumAddress(publickey)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)
        unicorn_txn = self.contract_instance.functions.SetUserInfo(account,objectkey).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def MakeClaim(self)
