pragma solidity ^0.4.0;

contract IdentityManager {

    struct Person {
	address Ehash;
	string StudentID;
        string tag;
	string role;
    }

    function IdentityManager() public{
    }

    mapping(bytes24 => Person) public user;
    mapping(address => bytes24) public UserMapping;
    
    function setNode(bytes24 Email, address e, string s, string t, string r){
	user[Email].Ehash = e;
	user[Email].StudentID = s;
	user[Email].tag = t;
	user[Email].role = r;
        UserMapping[e] = Email;
    }

    function setTag(bytes24 Email, string t){
        user[Email].tag = t;
    }

    function GetEhash(bytes24 person) constant returns (address) {
        return user[person].Ehash;
    }

    function GetInfo(bytes24 email) public returns (address,string,string,string) {
	return (user[email].Ehash,user[email].StudentID,user[email].tag,user[email].role);
    }

    function GetUserMapping(address Ehash) public returns (bytes24){
        return (UserMapping[Ehash]);
    }

}
