import base64
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

    def Kencode(self,key, clear):
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc).encode()).decode()
    def Kdecode(self,key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc).decode()
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)

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
    def GetEmailMapping(self,email):
        result = self.contract_instance.functions.GetEmailMapping(email).call()
        if result=='0x0000000000000000000000000000000000000000':
            return 'NoMapping'
        return result

    #def Register(self,account,publickey,objectkey,email):
    def Register(self,email,passwd,UTC,name,description,secret,country):
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
        SecretKey = self.api.object_put(io.BytesIO(json.dumps({"Data":secret}).encode()))['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,'Name',NameKey)['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,'Country',CountryKey)['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,'Description',DescriptionKey)['Hash']
        sharekey = objectkey
        objectkey = self.api.object_patch_add_link(objectkey,'Secret',SecretKey)['Hash']
        
        #objcetkey = self.Kencode(passwd,objectkey)

        account = self.GetAccount(email,passwd)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)

        unicorn_txn = self.contract_instance.functions.register(account,publickey,self.Kencode(passwd,objectkey),sharekey,email).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def GetUserInfo(self,email,passwd):
        if not self.EmailInUsed(email):
            return json.dumps({"status":"EmailNotExistedException"})
        account = self.GetAccount(email,passwd)
        objectkey = self.contract_instance.functions.GetUserInfo(account).call()
        objectkey = self.Kdecode(passwd,objectkey)
        results = self.api.object_get(objectkey)['Links']
        Odict = dict()
        for x in results:
            if x['Name'] == 'UTCBox':
                continue
            Odict[x['Name']] = self.api.object_get(x['Hash'])['Data']
        return json.dumps(Odict)

    def SetUserInfo(self,email,passwd,UTC,target,value):
        account = self.GetAccount(email,passwd)
        ValueKey = self.api.object_put(io.BytesIO(json.dumps({"Data":value}).encode()))['Hash']
        objectkey = self.contract_instance.functions.GetUserInfo(account).call()
        objectkey = self.Kdecode(passwd,objectkey)
        objectkey = self.api.object_patch_rm_link(objectkey,target)['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,target,ValueKey)['Hash']
        sharekey = self.contract_instance.functions.GetShareInfo(account).call()
        if target in {'Name','Country','Description'}: # Some target can be shared
            sharekey = self.api.object_patch_rm_link(sharekey,target)['Hash']
            self.api.object_patch_add_link(sharekey,target,ValueKey)['Hash']
        publickey = json.loads(UTC)['address']
        publickey = self.w3.toChecksumAddress(publickey)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)
        unicorn_txn = self.contract_instance.functions.SetUserInfo(account,self.Kencode(passwd,objectkey),sharekey).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def MakeClaim(self,email,passwd,UTC,subject,key,value):
        account = self.GetAccount(email,passwd)
        publickey = json.loads(UTC)['address']
        publickey = self.w3.toChecksumAddress(publickey)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)
        try:
            subject = self.w3.toChecksumAddress(subject)
        except:
            subject = publickey
        unicorn_txn = self.contract_instance.functions.MakeClaim(subject,key,value).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def GetUserClaim(self,issuer,index):
        Odict = dict()
        try:
            issuerAddress = self.GetEmailMapping(issuer)
            if issuerAddress != 'NoMapping': # _to is an email address
                issuer = issuerAddress
            issuer = self.w3.toChecksumAddress(issuer)
            result = self.contract_instance.functions.GetUserClaim(issuer,index).call()
            Odict['issuer'] = result[0]
            Odict['subject'] = result[1]
            Odict['key'] = result[2]
            Odict['value'] = result[3]
        except Exception as e:
            return json.dumps({"result":"GetUserClaimException", "log":str(e)})
        return json.dumps(Odict)

    def Approve(self,email,passwd,UTC,_to,_data):
        account = self.GetAccount(email,passwd)
        publickey = json.loads(UTC)['address']
        publickey = self.w3.toChecksumAddress(publickey)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)
        toAddress = self.GetEmailMapping(_to)
        if toAddress != 'NoMapping': # _to is an email address
            _to = toAddress
        _to = self.w3.toChecksumAddress(_to)
        DataKey = self.api.object_put(io.BytesIO(json.dumps({"Data":_data}).encode()))['Hash']
        unicorn_txn = self.contract_instance.functions.approve(_to,DataKey).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def GetUserAllowance(self,email,owner):
        ## Have to set Trigger User
        TriggerUser = self.w3.toChecksumAddress(self.GetEmailMapping(email))
        ownerAddress = self.GetEmailMapping(owner)
        if ownerAddress != 'NoMapping': # _to is an email address
            owner = ownerAddress
        owner = self.w3.toChecksumAddress(owner)
        result = self.contract_instance.functions.GetUserAllowance(owner).call({'from':TriggerUser})
        return json.dumps({"ApprovedFrom":owner, "Content": self.api.object_get(result)['Data']})

    def KeepUTC(self,email,passwd,UTC,UTCpasswd):
        if not self.EmailInUsed(email):
            return json.dumps({"status":"EmailNotExistedException"})
        account = self.GetAccount(email,passwd)
        publickey = json.loads(UTC)['address']
        publickey = self.w3.toChecksumAddress(publickey)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)
        objectkey = self.contract_instance.functions.GetUserInfo(account).call()
        objectkey = self.Kdecode(passwd,objectkey)
        UTCKey = self.api.object_put(io.BytesIO(json.dumps({"Data":self.Kencode(UTCpasswd,UTC)}).encode()))['Hash']
        objectkey = self.api.object_patch_add_link(objectkey,"UTCBox",UTCKey)['Hash']
        sharekey = self.contract_instance.functions.GetShareInfo(account).call()
        unicorn_txn = self.contract_instance.functions.SetUserInfo(account,self.Kencode(passwd,objectkey),sharekey).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def ReceiveUTC(self,email,passwd,UTCpasswd):
        if not self.EmailInUsed(email):
            return json.dumps({"status":"EmailNotExistedException"})
        account = self.GetAccount(email,passwd)
        objectkey = self.contract_instance.functions.GetUserInfo(account).call()
        objectkey = self.Kdecode(passwd,objectkey)
        results = self.api.object_get(objectkey)['Links']
        for x in results:
            if x['Name'] == 'UTCBox':
                UTC = self.api.object_get(x['Hash'])['Data']
                break
        return self.Kdecode(UTCpasswd,UTC)

    ###############################################################################

    def sendEther(self,passwd,UTC,receiver_email,_value):
        sender = json.loads(UTC)['address']
        sender = self.w3.toChecksumAddress(sender)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)
        To = self.GetEmailMapping(receiver_email)
        if To == 'NoMapping':
            try:
                To = self.w3.toChecksumAddress(receiver_email)
            except:
                return json.dumps({"status": "ERROR", "log": "No email mapping and not an address."})
        else:
            To = self.w3.toChecksumAddress(To)
        signed_txn = self.w3.eth.account.signTransaction(dict(
            nonce = self.w3.eth.getTransactionCount(sender),
            gasPrice = self.w3.eth.gasPrice,
            gas=100000,
            #to = self.w3.toChecksumAddress(self.GetEmailMapping(receiver_email)),
            to = To,
            value = self.w3.toWei(_value, "ether"),
            data=b'',
        ),
            private_key,
        )
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def BecomeFriend(self,email,passwd,UTC,friend_address):
        account = self.GetAccount(email,passwd)
        Faddress = self.GetEmailMapping(friend_address)
        if Faddress != 'NoMapping': # friend_address is an email address
            friend_address = Faddress
        friend_address = self.w3.toChecksumAddress(friend_address)
        publickey = json.loads(UTC)['address']
        publickey = self.w3.toChecksumAddress(publickey)
        private_key = self.w3.eth.account.decrypt(UTC, passwd)
        unicorn_txn = self.contract_instance.functions.BecomeFriend(account,friend_address).buildTransaction({'nonce':self.w3.eth.getTransactionCount(publickey)})
        signed_txn = self.w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def GetFriendInfo(self,email,friend_address):
        ## Have to set Trigger User
        TriggerUser = self.w3.toChecksumAddress(self.GetEmailMapping(email))
        Faddress = self.GetEmailMapping(friend_address)
        if Faddress != 'NoMapping': # friend_address is an email address
            friend_address = Faddress
        friend_address = self.w3.toChecksumAddress(friend_address)
        sharekey = self.contract_instance.functions.GetFriendInfo(friend_address).call({'from':TriggerUser})
        results = self.api.object_get(sharekey)['Links']
        Odict = dict()
        for x in results:
            Odict[x['Name']] = self.api.object_get(x['Hash'])['Data']
        return json.dumps(Odict)

    def decode_contract_call(self,contract_abi: list, TID: str): 
        Transaction = self.w3.eth.getTransaction(TID)
        call_data = str(Transaction.input)
        call_data_bin = decode_hex(call_data) 
        method_signature = call_data_bin[:4] 
        for description in contract_abi: 
            if description.get('type') != 'function': 
                continue 
            method_name = normalize_abi_method_name(description['name']) 
            arg_types = [item['type'] for item in description['inputs']] 
            method_id = get_abi_method_id(method_name, arg_types) 
            if zpad(encode_int(method_id), 4) == method_signature: 
                try: 
                    args = decode_abi(arg_types, call_data_bin[4:]) 
                except AssertionError: 
                    # Invalid args 
                    continue 
                return method_name, args
