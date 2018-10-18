# coding=utf-8
import IDToyFramework
import sys

email = 'yenkuanlee@gmail.com'
passwd = 'password'
UTC = 'UTC file content'
name = '李彥寬'
description = 'handsome'
secret = 'I am 70 KG.'
country = 'Taiwan'
god = '0x42946c2bb22ad422e7366d68d3ca07fb1862ff36'
dog = '0xe6ab871f860d9f28764d5d2e0672396a7643710e'

email2 = 'kevin800405@yahoo.com.tw'
passwd2 = 'password2'
UTC2 = 'UTC2 file content'
name2 = 'joker'
description2 = 'sombody'
secret2 = 'Sit down please.'


a = IDToyFramework.IDToyFramework()

#print(a.Register(email,passwd,UTC,name,description,secret,country))
#print(a.Register(email2,passwd2,UTC2,name2,description2,secret2,country))

#print(a.GetUserInfo(email,passwd))
#print(a.SetUserInfo(email,passwd,UTC,'Secret','I am 68 KG now.'))
#print(a.MakeClaim(email,passwd,UTC,'','Kevin','I am hungry.'))
#print(a.GetUserClaim(god,0))
#print(a.KeepUTC(email,passwd,UTC,'utcpasswd'))
#print(a.ReceiveUTC(email,passwd,'utcpasswd'))
#print(a.Approve(email,passwd,UTC,dog,'go to eat.'))
#print(a.GetUserAllowance(god))
#print(a.GetEmailMapping(email))

#print(a.sendEther(passwd,UTC,'kevin800405@yahoo.com.tw',123))
#print(a.BecomeFriend(email,passwd,UTC,dog))
#print(a.GetFriendInfo(god))
