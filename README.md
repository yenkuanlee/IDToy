# IDToy
Demo: 會員身份 Smart Contract
1. 用 Solidity 寫，具備基本的會員系統功能：註冊、編輯個人資料、聲明、授權、恢復私鑰。
2. 可參考 uport。

加分項：
1. 增加付款與加好友功能。
2. 對自己寫的 Smart Contract 做安全稽核，有哪些安全漏洞？
3. 把自己寫的合約 deploy 到 Ethereum 的測試鏈。

## 程式簡介
- contract/IdentityManager.sol : 智能合約
- contract/deploy_contract.py : 將合約發布上鏈
- contract/contract.json : 合約資訊, 包含abi與合約地址
- IDToyFramework.py : web3程式, 觸發智能合約
- example.py : 範例程式, 包含各功能執行方式


## 環境
- 本專案開發環境為Ethereum私有鏈, 共識機制為POA
- python3.6
- web3.py 4.x
- solidity 0.4.x
- ipfs 0.4.x

## 使用說明
### 發布合約
在contract目錄底下將IdentityManager.sol合約發布上鏈, 同目錄會產生contract.json, 用來記錄合約資訊
```
$ cd contract
$ python3 deploy_contract.py
```
### 使用
- 在example.py中導入IDToyFramework, 便可開始使用各項功能, 下一段會針對所有功能進一步解說
- example.py中的參數可先填入, 以利後續操作, 下一段會詳細說明個參數意義
```
email = 'yenkuanlee@gmail.com'                      # 第一個帳戶綁定的email
passwd = 'password'                                 # 第一個帳戶的密碼
UTC = 'UTC file content'                            # 第一個帳戶的UTC file內容
name = '李彥寬'                                      # 第一個帳戶的使用者名字
description = 'handsome'                            # 第一個帳戶使用者的描述
secret = 'I am 70 KG.'                              # 第一個帳戶使用者的秘密欄位
country = 'Taiwan'                                  # 第一個帳戶使用者的國家
god = '0x42946c2bb22ad422e7366d68d3ca07fb1862ff36'  # 第一個帳戶的address
dog = '0xe6ab871f860d9f28764d5d2e0672396a7643710e'  # 第二個帳戶的address
email2 = 'kevin800405@yahoo.com.tw'                 # 第二個帳戶綁定的email
passwd2 = 'password2'                               # 第二個帳戶的密碼
UTC2 = 'UTC2 file content'                          # 第二個帳戶的UTC file內容
name2 = 'joker'                                     # 第二個帳戶的使用者名字
description2 = 'sombody'                            # 第二個帳戶使用者的描述
secret2 = 'Sit down please.'                        # 第二個帳戶使用者的秘密欄位


import IDToyFramework
a = IDToyFramework.IDToyFramework()
```

## 功能與邏輯解說
### 註冊
```
# IDToyFramework.Register
def Register(self,email,passwd,UTC,name,description,secret,country)
```
#### 參數
- 使用email註冊
- password為以太錢包的密碼
- UTC為私鑰檔內容, json格式
- name, description, country為使用者相關資訊, 參考uport欄位
- secret為使用者叫隱私的資訊, 後續說明
#### 智能合約結構
  - 每個使用者資訊存入Person結構, 包含以下項目
    - PublicKey ： 用以太錢包address代表
    - ObjectKey ： 將所有使用者資訊帶入ipfs merkle tree, 取得root key再用passwd加密
    - ShareKey ： 可分享給好友的資訊, 帶入ipfs merkle tree取得的root key
  - 合約中利用mapping(account=>Person)紀錄所有使用者資訊, account透過email及passwd加密
  - 使用者email與PublicKey為一對一對應
#### 範例
```
# 註冊第一個帳戶
a.Register(email,passwd,UTC,name,description,secret,country)

# 註冊第二個帳戶
a.Register(email2,passwd2,UTC2,name2,description2,secret2,country)
```
### 使用者資訊
```
a.GetUserInfo(email,passwd)
```
### 編輯個人資料
```
a.SetUserInfo(email,passwd,UTC,'Secret','I am 68 KG now.')
```
### 聲明
```
a.MakeClaim(email,passwd,UTC,'','Kevin','I am hungry.')
```
### 聲明資訊
```
a.GetUserClaim(god,0)
```
### 授權
```
a.Approve(email,passwd,UTC,dog,'go to eat.')
```
### 授權資訊
```
a.GetUserAllowance(god)
```
### 保存私鑰
```
a.KeepUTC(email,passwd,UTC,'utcpasswd')
```
### 恢復私鑰
```
a.ReceiveUTC(email,passwd,'utcpasswd')
```
### 付款
```
a.sendEther(passwd,UTC,'kevin800405@yahoo.com.tw',123)
```
### 成為好友
```
a.BecomeFriend(email,passwd,UTC,dog)
```
### 好友資訊
```
a.GetFriendInfo(god)
```

## 智能合約安全稽核

## Ethereum 測試鏈

## Reference
- uport
  - [Github : uport-project](https://github.com/uport-project)
  - [簡介](https://www.jianshu.com/p/12a2454440bf)
  - [Medium : Private Data on Public Networks](https://medium.com/uport/private-data-on-public-networks-ab1086a137d8)
- claim in ERC780
  - [Github : ethereum-claims-registry](https://github.com/uport-project/ethereum-claims-registry/blob/master/contracts/EthereumClaimsRegistry.sol)
  - [Reddit : ERC 780: Ethereum Claim Registry](https://www.reddit.com/r/ethereum/comments/7gewn7/erc_780_ethereum_claim_registry/)
- approve in ERC725
  - [CSDN : ERC725詳細說明](https://blog.csdn.net/diandianxiyu_geek/article/details/79467671)
