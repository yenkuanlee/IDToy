import ipfsapi
import json
import requests
import subprocess
from subprocess import Popen
import threading
import time

def IpfsDaemon():
    cmd = "ipfs daemon"
    try:
        p = Popen(cmd.split(),stdout=subprocess.PIPE)
        time.sleep(2)
        fw = open('ipfs.pid','w')
        fw.write(str(p.pid))
        fw.close()
        while True:
            line = p.stdout.readline().decode("utf-8").replace("\n","")
            print(line)
            if "Daemon is ready" == line:
                print("IPFS START.\n")
                break
        print(json.dumps({"status":"SUCCESS"}))
    except Exception as e:
        print(json.dumps({"status":"ERROR", "log":str(e)}))

def gethDaemon():
    cmd = "geth --datadir ./kevin --networkid 18 --port 28000 --rpc --rpcaddr 127.0.0.1 --rpcport 3000 --rpcapi 'net,eth,web3,miner,personal,db' --rpccorsdomain '*'"
    try:
        p = Popen(cmd.split(),stdout=subprocess.PIPE)
        time.sleep(2)
        fw = open('geth.pid','w')
        fw.write(str(p.pid))
        fw.close()
        print(json.dumps({"status":"SUCCESS"}))
    except Exception as e:
        print(json.dumps({"status":"ERROR", "log":str(e)}))

# START IPFS
Ithread = threading.Thread(target=IpfsDaemon, name='ipfs')
Ithread.start()

# GET PRIVATE KEY FROM IPFS
r = requests.get('https://ipfs.io/ipfs/QmZgYuiRVLNX5ApLpmq3KXDXpTECLuKtEG7XDVswR6JThw')
fw = open('./kevin/keystore/god','w')
fw.write(r.text)
fw.close()

# START GETH
Gthread = threading.Thread(target=gethDaemon, name='geth')
Gthread.start()

# Start Mining
while True:
    cmd = "geth attach http://localhost:3000 --exec \"miner.start(2)\""
    try:
        output = subprocess.check_output(cmd, shell=True).decode("utf-8").replace("\n","")
        print("KEVIN MINER OUTPUT : "+output)
        if output == "null":
            break
        time.sleep(5)
    except:
        print("KEVIN MINER WAIT 10")
        time.sleep(5)
        continue

# GET TEST CODE FROM IPFS
r = requests.get('https://ipfs.io/ipfs/QmdcgD77hdm2xFymsJtyU7x73bzMnJfq5Y6bRpTasdaSXk')
fw = open('./test.py','w')
fw.write(r.text)
fw.close()
