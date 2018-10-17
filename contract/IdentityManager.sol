pragma solidity ^0.4.0;

contract IdentityManager {

    struct Person {
	address PublicKey;
        string ObjectKey;
    }

    function IdentityManager() public{
    }

    mapping(bytes32 => Person) public user;
    mapping(address => string) public UserMapping;
    
    function register(bytes32 account, address publickey, string objectkey, string email){
	user[account].PublicKey = publickey;
	user[account].ObjectKey = objectkey;
        UserMapping[publickey] = email;
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
