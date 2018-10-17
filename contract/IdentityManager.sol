pragma solidity ^0.4.0;

contract IdentityManager {

    struct Person {
	address PublicKey;
        string ObjectKey;
    }

    function IdentityManager() public{
    }

    function stringsEqual(string storage _a, string memory _b) internal constant returns (bool) {
        bytes storage a = bytes(_a);
        bytes memory b = bytes(_b);
        if (a.length != b.length)
            return false;
        for (uint i = 0; i < a.length; i ++)
            if (a[i] != b[i])
                return false;
        return true;
    }

    mapping(bytes32 => Person) public user;
    mapping(address => string) public UserMapping;
    string[] UserList;

    function EmailInUsed(string email) public returns (bool){
        for(uint i=0;i<UserList.length;i++)
            if(stringsEqual(UserList[i],email))
                return true;
        return false;
    }

    function AddressInUsed(address publickey) public returns (bool){
        if(stringsEqual(UserMapping[publickey],''))
            return false;
        return true;
    }
    
    function register(bytes32 account, address publickey, string objectkey, string email){
        if(EmailInUsed(email))
            return;
        if(AddressInUsed(publickey))
            return;
	user[account].PublicKey = publickey;
	user[account].ObjectKey = objectkey;
        UserMapping[publickey] = email;
        UserList.push(email);
    }

    function GetUserInfo(bytes32 account) public returns (string) {
	return user[account].ObjectKey;
    }

    function SetUserInfo(bytes32 account, string new_objectkey){
        user[account].ObjectKey = new_objectkey;
    }

    function GetUserMapping(address publickey) public returns (string){
        return (UserMapping[publickey]);
    }

}
