import datetime
import io
import ipfsapi
import json
from web3 import Web3, HTTPProvider, TestRPCProvider
import os
from web3.middleware import geth_poa_middleware
from ethereum.abi import (
    decode_abi,
    normalize_name as normalize_abi_method_name,
    method_id as get_abi_method_id)
from ethereum.utils import encode_int, zpad, decode_hex
import requests

Cpath = os.path.dirname(os.path.realpath(__file__))
f = open(Cpath+'/mcoin.conf','r')
Cdict = dict()
while True:
    line = f.readline()
    if not line:break
    line = line.replace("\n","")
    line = line.replace(" ","")
    line = line.split("#")[0]
    try:
        tmp = line.split("=")
        Cdict[tmp[0]] = tmp[1]
    except:
        pass
f.close()

Lhost = Cdict['Lhost']
SuperAccount = Cdict['SuperAccount']
ERC20contract_address = Cdict['ERC20contract_address']
ProjectPath = Cdict['ProjectPath']
IPFS_IP = Cdict['IPFS_IP']
IPFS_PORT = Cdict['IPFS_PORT']


EmailWhiteList = ['yenkuanlee@gmail.com','luhaoming@gmail.com', '1061275', '05170445', '8100464']
Edict = dict()
Edict['User'] = ProjectPath+"/User/users.json"
Edict['Application'] = ProjectPath+"/Application/app.json"
Edict['Balance'] = ProjectPath+"/Balance/abi"

class EthWeb3Framework:
    def __init__(self):
        self.api = ipfsapi.connect(IPFS_IP,IPFS_PORT)
        self.w3 = Web3(HTTPProvider('http://localhost:3000'))
        self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        ### Element contract
        f = open(Edict["User"],'r')
        line = f.readline()
        Jline = json.loads(line)
        f.close()
        self.abi = Jline['abi']
        contract_address = Jline['contract_address']
        self.contract_instance = self.w3.eth.contract(abi=self.abi, address=contract_address)
        ### ERC20 contract
        f = open(Edict['Balance'],'r')
        line = f.readline()
        self.ERC20abi = json.loads(line)
        f.close()
        self.ERC20contract_instance = self.w3.eth.contract(abi=self.ERC20abi, address=self.w3.toChecksumAddress(ERC20contract_address))

    ## Balance
    def GetBalance(self,Ehash):
        try:
            address = self.w3.toChecksumAddress(Ehash)
            result = self.ERC20contract_instance.functions.balanceOf(address).call()
            return result
        except:
            return "GetBalanceFailed"
    def GetAllowance(self,Ehash):
        try:
            SuperAccountX = self.w3.toChecksumAddress(SuperAccount)
            address = self.w3.toChecksumAddress(Ehash)
            result = self.ERC20contract_instance.functions.allowance(SuperAccountX,address).call()
            return result
        except:
            return "GetAllowanceFailed"

    ## User
    def GetInfo(self,Email):
        Odict = dict()
        Odict['Email'] = Email
        try:
            Email = self.w3.toBytes(text=Email)
            result = self.contract_instance.functions.GetInfo(Email).call()
            Odict['Ehash'] = result[0]
            Odict['StudentID'] = result[1]
            try:
                Odict['TransactionRecord'] = self.api.object_get(result[2])
                Odict['Name'] = Odict['TransactionRecord']['Data']
            except:
                Odict['TransactionRecord'] = "GetTransactionRecordFailed"
            Odict['role'] = result[3]
            try:
                nounce = self.w3.eth.getTransactionCount(self.w3.toChecksumAddress(Odict['Ehash']))
                Odict['nounce'] = nounce
            except:
                Odict['nounce'] = "GetNonceFailed"
            Odict['Balance'] = self.GetBalance(Odict['Ehash'])
            Odict['Allowance'] = self.GetAllowance(Odict['Ehash'])
            if Odict['Ehash']=='0x0000000000000000000000000000000000000000' and Odict['TransactionRecord'] == 'GetTransactionRecordFailed' and Odict['StudentID']=='' and Odict['role']=='':
                return {"status":"NotExistedException"}
            if result[2][0]=="Q":
                Odict['UserStatus'] = 0
            else:
                Odict['UserStatus'] = result[2][0]
            Odict['status'] = "SUCCESS"
            return Odict
        except Exception as e:
            return {"status":"GetInfoFailed", "log":str(e)}

    def UserMapping(self,Ehash):
        Ehash = self.w3.toChecksumAddress(Ehash)
        result = self.contract_instance.functions.GetUserMapping(Ehash).call().decode("utf-8")
        return result.replace("\x00","")

    def SetUser(self,Email,Ehash,StudentID,role,name=False):
        if not name:
            name = Email
        info = self.GetInfo(Email)
        if Email in EmailWhiteList:
            pass
        elif info['status']!='NotExistedException':
            return {"status":"EmailAlreadyUsedException"}
        elif self.UserMapping(Ehash)!="":
            return {"status":"EhashAlreadyUsedException"}
        account = self.w3.toChecksumAddress(SuperAccount)
        Tbyte = json.dumps({"Data":name}).encode()
        StringEmail = Email
        Email = self.w3.toBytes(text=Email)
        Ehash = self.w3.toChecksumAddress(Ehash)
        tag = self.api.object_put(io.BytesIO(Tbyte))['Hash']
        self.api.pin_add(tag)
        try:
            self.w3.personal.unlockAccount(account,"123")
            self.contract_instance.functions.setNode(Email,Ehash,StudentID,tag,role).transact({'from': account})
            TID = self.w3.eth.sendTransaction({'to': Ehash, 'from': account, 'value': self.w3.toWei(100, "ether")})
            return {"status":"SUCCESS", "TID":TID.hex()}
        except:
            return {"status":"SetUserFailed"}

    def SetUserStatus(self,Email,Ustatus):
        try:
            Email = self.w3.toBytes(text=Email)
            result = self.contract_instance.functions.GetInfo(Email).call()
            tag = result[2]
            tag = Ustatus[0]+tag[1:]
            if Ustatus=="0":
                tag = "Q"+tag[1:]
            SuperAccountX = self.w3.toChecksumAddress(SuperAccount)
            self.w3.personal.unlockAccount(SuperAccountX,"123")
            TID = self.contract_instance.functions.setTag(Email,tag).transact({'from': SuperAccountX})
            #return {"status":"SUCCESS", "TID":TID.hex()}
        except Exception as e:
            return {"status":"SetUserStatusFailed", "log":str(e)}
        try:
            swarm = self.api.swarm_peers()
            IPList = [Lhost]
            for x in swarm['Peers']:
                IPList.append(x['Addr'].split("/")[2])
            for x in IPList:
                user_info = {"Email":StringEmail}
                r = requests.post("http://"+x+":5000/Lusers/InsertLusers", data=user_info)
            return {"status":"SUCCESS", "TID":TID.hex()}
        except Exception as e:
            return {"status": "InsertLuserFailed", "log": str(e)}

    ## Input Decoder
    def decode_contract_call(self,contract_abi: list, call_data: str):
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

    def Decoder(self,TID):
        Transaction = self.w3.eth.getTransaction(TID)
        result = self.decode_contract_call(self.ERC20abi,Transaction.input)
        if result[0]!="transfer" and result[0]!="transferFrom":
            return {"status":"NotTransferException"}
        Rdict = dict()
        Rdict['sender'] = self.UserMapping(Transaction['from'])
        Rdict['receiver'] = self.UserMapping(result[1][0])
        Rdict['mcoin'] = result[1][1]
        if result[0]=="transfer":
            return [self.UserMapping(Transaction['from']),self.UserMapping(result[1][0]),result[1][1],result[0]]
        elif result[0]=="transferFrom":
            return [self.UserMapping(Transaction['from']),self.UserMapping(result[1][1]),result[1][2],result[0]]

    ## Transaction
    def Trecord(self,Email,T):
        result = self.contract_instance.functions.GetInfo(self.w3.toBytes(text=Email)).call()
        ObjectHash = result[2]
        Tbyte = json.dumps({"Data":T}).encode()
        Thash = self.api.object_put(io.BytesIO(Tbyte))['Hash']
        self.api.pin_add(Thash)
        tag = self.api.object_patch_add_link(ObjectHash,T,Thash)['Hash']
        SuperAccountX = self.w3.toChecksumAddress(SuperAccount)
        self.w3.personal.unlockAccount(SuperAccountX,"123")
        TID = self.contract_instance.functions.setTag(self.w3.toBytes(text=Email),tag).transact({'from': SuperAccountX})
        return {"status":"SUCCESS","TID":TID.hex()}

    def sendRawTransaction(self,Rhash):
        Tlist = list()
        tmp = Rhash.split(",")
        for x in tmp:
            T = self.w3.eth.sendRawTransaction(x)
            Transaction = self.w3.eth.getTransaction(T)
            Tlist.append(str(T.hex()))
        for x in Tlist:
            Tinfo = self.Decoder(x)
            try:
                Tinfo.append(str(datetime.datetime.now()).replace(" ","T"))
                Tinfo.append(x)
                self.Trecord(Tinfo[0],json.dumps(Tinfo).replace("\\u0000",""))
                self.Trecord(Tinfo[1],json.dumps(Tinfo).replace("\\u0000",""))
            except: # not call erc20 function, return dict({"status": "NotTransferException"})
                continue
        return Tlist

    def CheckTransaction(self,TID):
        try:
            result = self.Decoder(TID)
            TransactionReceipt = self.w3.eth.getTransactionReceipt(TID)
            Rdict = dict()
            Rdict['status'] = "SUCCESS"
            Rdict['sender'] = result[0]
            Rdict['receiver'] = result[1]
            Rdict['mcoin'] = result[2]
            try:
                Rdict['TransactionStatus'] = TransactionReceipt['status']
            except:
                Rdict['TransactionStatus'] = '0'
            return json.loads(json.dumps(Rdict).replace("\\u0000",""))
        except Exception as e:
            return {"status": "ERROR", "log": str(e), "TID": str(TID)}
