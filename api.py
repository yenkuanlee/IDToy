from flask import Flask
from flask import request
from flask_cors import CORS
import os
import requests
import subprocess
import json
import time
import hashlib
import ipfsapi
import io
import sqlite3
import EthWeb3Framework

app = Flask(__name__)
CORS(app, resources=r'/*')

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
SuperEmail = Cdict['SuperEmail']
ProjectPath = Cdict['ProjectPath']
IPFS_IP = Cdict['IPFS_IP']
IPFS_PORT = Cdict['IPFS_PORT']
PicturePath = Cdict['PicturePath']
PictureBias = Cdict['PictureBias']
LusersPath = Cdict['LusersPath']
AppStorePath = Cdict['AppStorePath']

@app.route('/')
def index():
    return "Hello World!!"

@app.route('/Login', methods=['POST'])
def login():
    account = request.form['account']
    passwd = request.form['passwd']
    m = hashlib.md5()
    ts = str(int(time.time()))
    m.update(("MCU"+passwd+account+ts).encode('utf-8'))
    h = m.hexdigest()
    Odict = dict()
    Odict['account'] = account
    Odict['token'] = h
    Odict['timestamp'] = ts
    return json.dumps(Odict)

@app.route('/SetUserX', methods=['POST'])
def set_userX():
    Email = request.form['Email']
    Ehash = request.form['Ehash']
    StudentID = request.form['StudentID']
    role = request.form['role']
    try:
        Name = request.form['Name']
    except:
        Name = request.form['Email']
    Jinfo = {'account':Email}
    r = requests.post("http://120.125.73.108:5000/GetSUstatus", data=Jinfo)
    SUstatus = json.loads(r.text)
    if SUstatus['status']:
        a = EthWeb3Framework.EthWeb3Framework()
        result = a.SetUser(Email,Ehash,StudentID,role,Name)
        return json.dumps(result)
    else:
        return json.dumps({"status": "PleaseLoginFirstException"})

@app.route('/GetInfoX', methods=['POST'])
def get_infoX():
    Email = request.form['Email']
    a = EthWeb3Framework.EthWeb3Framework()
    return json.dumps(a.GetInfo(Email))

@app.route('/sendRawTransactionX', methods=['POST'])
def send_raw_transactionX():
    RAW_TRANSACTION = request.form['RAW_TRANSACTION']
    a = EthWeb3Framework.EthWeb3Framework()
    result = a.sendRawTransaction(RAW_TRANSACTION)
    return json.dumps(result)

@app.route('/CheckTransactionX', methods=['POST'])
def check_transactionX():
    TID = request.form['TID']
    a = EthWeb3Framework.EthWeb3Framework()
    result = a.CheckTransaction(TID)
    return json.dumps(result)

if __name__ == '__main__':
    app.run(host=Lhost, debug=True)
