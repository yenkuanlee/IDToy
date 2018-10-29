# coding=utf-8
import IDToyFramework
import json
import sys

email = 'yenkuanlee@gmail.com'
passwd = 'password'
UTC = ''
name = '李彥寬'
description = 'handsome'
secret = 'I am 70 KG.'
country = 'Taiwan'

email2 = 'kevin800405@yahoo.com.tw'
passwd2 = 'password'
UTC2 = ''
name2 = 'joker'
description2 = 'sombody'
secret2 = 'Sit down please.'


a = IDToyFramework.IDToyFramework()

#print(a.Register(email,passwd,UTC,name,description,secret,country))
#print(a.Register(email2,passwd2,UTC2,name2,description2,secret2,country))

#print(a.GetUserInfo(email,passwd))
#print(a.SetUserInfo(email,passwd,UTC,'Secret','I am 68 KG now.'))
#print(a.MakeClaim(email,passwd,UTC,'','Kevin','I am hungry.'))
#print(a.GetUserClaim(email,0))
#print(a.KeepUTC(email,passwd,UTC,'utcpasswd'))
#print(a.ReceiveUTC(email,passwd,'utcpasswd'))
#print(a.Approve(email2,passwd2,UTC2,email,'go to eat shit.'))
#print(a.GetUserAllowance(email,email2))
#print(a.GetEmailMapping(email2))

#print(a.sendEther(passwd,UTC,email2,0.1))
#print(a.BecomeFriend(email2,passwd2,UTC2,email))
#print(a.GetFriendInfo(email2,email))


#f = open('contract/contract.json','r')
#Jbi = json.loads(f.readline())['abi']
#print(a.decode_contract_call(Jbi,sys.argv[1]))
