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
- 參數
  - 使用email註冊
  - password為以太錢包的密碼
  - UTC為私鑰檔內容, json格式
  - name, description, country為使用者相關資訊, 參考uport欄位
  - secret為使用者叫隱私的資訊, 後續說明
- 智能合約結構
  - 每個使用者資訊存入Person結構, 包含以下項目
    - PublicKey ： 用以太錢包address代表
    - ObjectKey ： 將所有使用者資訊帶入ipfs merkle tree, 取得root key再用passwd加密
    - ShareKey ： 可分享給好友的資訊, 帶入ipfs merkle tree取得的root key
  - 合約中利用user紀錄所有使用者資訊,其資料結構為mapping(bytes32=>Person), 當中mapping key是透過email及passwd加密
  - 使用者email與PublicKey為一對一對應
    - 合約會判定重複註冊的情況
- 回傳
  - 執行合約的Transaction ID
- 範例
```
# 註冊第一個帳戶
a.Register(email,passwd,UTC,name,description,secret,country)

執行結果
0xdd745ea81e3bd82efb8e4b38d4f15ad2d437ebdab6900688ffc38944e974fb2a

# 註冊第二個帳戶
a.Register(email2,passwd2,UTC2,name2,description2,secret2,country)

執行結果
0x6f50cda79f38804a2657b0b3fc913c8dcc5fbb546dac17457b04bcb398bf8ae9
```
### 使用者資訊
使用者可看到自己的資訊
```
# IDToyFramework.GetUserInfo
def GetUserInfo(self,email,passwd)
```
- 參數
  - 登入使用者的email與passwd
- 智能合約
  - 將email與passwd加密後送給智能合約, 取得使用者的ObjectKey
- 回傳
  - 將ObjectKey解密, 取得merkle tree上的資訊並結構化, 回傳為json格式
- 範例
```
a.GetUserInfo(email,passwd)

執行結果
{"Name": "\u674e\u5f65\u5bec", "Country": "Taiwan", "Description": "handsome", "Secret": "I am 70 KG."}
```
### 編輯個人資料
使用者可修改個人資料
```
# IDToyFramework.SetUserInfo
def SetUserInfo(self,email,passwd,UTC,target,value)
```
- 參數
  - email, passwd, UTC為使用者登入資訊
  - target為使用者可修改資料的欄位, 包含Name, Country, Description, Secret
  - value為要修改的內容
- 智能合約
  - 取得user ObjectKey, 解密取得meklre tree, 修整枝葉後再將新的ObjectKey存回合約中
- 回傳
  - 執行合約的Transaction ID
- 範例
```
a.SetUserInfo(email,passwd,UTC,'Secret','I am 68 KG now.')

執行結果
0x821240326bfb7c1bdb2634a8eccc1aefe98f164b7b9d4ea1d3409bee395aaed8

a.GetUserInfo(email,passwd)

執行結果
{"Description": "handsome", "Name": "\u674e\u5f65\u5bec", "Country": "Taiwan", "Secret": "I am 68 KG now."}
```
### 聲明
使用者可發表聲明
```
# IDToyFramework.MakeClaim
def MakeClaim(self,email,passwd,UTC,subject,key,value)
```
- 參數
  - email, passwd, UTC為使用者登入資訊
  - subject,key,value為聲明相關欄位
- 智能合約
  - 用Claim結構紀錄使用者聲名, 參考ERC780, 共有4個項目
    - address Issuer ： 發表聲明的人
    - address Subject ： 與聲明相關的人, 若空值則為聲明人
    - string Key ： 聲明主題
    - string Value ： 聲明內容
  - 使用mapping(address => Claim[]) UserClaim紀錄所有使用者的聲名
- 回傳
  - 執行合約的Transaction ID
- 範例
```
a.MakeClaim(email,passwd,UTC,'','Kevin','I am hungry.')

執行結果
0x7610654d7cf2c0982e2c6be70de7967df02e025015a4c1b65b3f883b1dbc457a
```
### 聲明資訊
使用者可察看任何人的聲明資訊
```
# IDToyFramework.GetUserClaim
def GetUserClaim(self,issuer,index)
```
- 參數
  - issuer為發表聲明人的address
  - index可當issuer的某個聲明的ID
- 智能合約
  - 從UserClaim中取得使用者聲明4個項目的內容
- 回傳
  - 將合約回傳整理成json格式回傳
- 範例
```
a.GetUserClaim(god,0)

執行結果
{"subject": "0x42946C2Bb22ad422e7366d68d3Ca07fB1862ff36", "key": "Kevin", "value": "I am hungry.", "issuer": "0x42946C2Bb22ad422e7366d68d3Ca07fB1862ff36"}
```
### 授權
使用者可對某人授權
```
# IDToyFramework.Approve
def Approve(self,email,passwd,UTC,_to,_data)
```
- 參數
  - email, passwd, UTC為使用者登入資訊
  - _to為授權對象
  - _data為授權內容
- 智能合約
  - 參考ERC20的Approve(token授權), 以及ERC725的Approve
  - mapping(address => mapping (address => string)) allowed 紀錄, 誰授權給誰什麼內容
  - 授權內容會放在ipfs的一個object node中, 增加彈性
- 回傳
  - 執行合約的Transaction ID
- 範例
```
a.Approve(email,passwd,UTC,dog,'go to eat.')

執行結果
0xd46b5b47af832b67d52a1b2f09203ded3f549ca871c6719571e598293e8032c4
```
### 授權資訊
使用可查詢被某人授權的內容
```
# IDToyFramework.GetUserAllowance
def GetUserAllowance(self,owner)
```
- 參數
  - owner : 授權人的Address
- 智能合約
  - 從allowed中取得執行合約人被owner授權的_data
- 回傳
  - 透過_data取得merkle tree中的content, 整理成json
    - ApprovedFrom ： 授權人Address
    - Content : 授權內容
- 範例
```
a.GetUserAllowance(god)

執行結果
{"ApprovedFrom": "0x42946C2Bb22ad422e7366d68d3Ca07fB1862ff36", "Content": "go to eat."}
```
### 保存私鑰
```
# IDToyFramework.KeepUTC
def KeepUTC(self,email,passwd,UTC,UTCpasswd)
```
- 參數
  - email, passwd, UTC為使用者登入資訊
  - UTC為要保存的私鑰內容
  - UTCpasswd為保存私鑰的密碼, 日後想取回私鑰需要這組密碼
- 智能合約
  - 取得使用者的ObjectKey並解密取得merkle tree內容, 將UTC透過UTCpasswd加密後, 插入merkle tree中, 欄位為UTCBox
- 回傳
  - 執行合約的Transaction ID
- 範例
```
a.KeepUTC(email,passwd,UTC,'utcpasswd')

執行結果
0xecbb08d4f0e8ea0d2c9745d12c4e4945da59d5e96219c9bf86ecf6110169e7ee
```
### 恢復私鑰
```
# IDToyFramework.ReceiveUTC
def ReceiveUTC(self,email,passwd,UTCpasswd)
```
- 參數
  - email, passwd為使用者登入資訊
  - UTCpasswd為取回私鑰的密碼
- 智能合約
  - 取得使用者的ObjectKey, 一連串解密後取得UTC內容
- 回傳
  - 私鑰內容
- 範例
```
a.ReceiveUTC(email,passwd,'utcpasswd')

執行結果
{"address":"42946c2bb22ad422e7366d68d3ca07fb1862ff36","crypto":{"cipher":"xxx","ciphertext":"xxx","cipherparams":{"iv":"xxx"},"kdf":"xxx","kdfparams":{"dklen":xxx,"n":xxx,"p":xxx,"r":xxx,"salt":"xxx"},"mac":"xxx"},"id":"xxx","version":xxx}
```
### 付款
- 參數
- 智能合約
- 回傳
- 範例
```
a.sendEther(passwd,UTC,'kevin800405@yahoo.com.tw',123)
```
### 成為好友
- 參數
- 智能合約
- 回傳
- 範例
```
a.BecomeFriend(email,passwd,UTC,dog)
```
### 好友資訊
- 參數
- 智能合約
- 回傳
- 範例
```
a.GetFriendInfo(god)
```
### 其他功能
- Address查Email
- Email查Address
- GetAccount

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
