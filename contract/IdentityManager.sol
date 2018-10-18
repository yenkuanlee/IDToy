pragma solidity ^0.4.0;

contract IdentityManager {

    struct Person {
	address PublicKey;
        string ObjectKey;
    }

    struct Claim{
        address Issuer;
        address Subject;
        string Key;
        string Value;
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

    function stringToBytes32(string memory source) returns (bytes32 result) {
        bytes memory tempEmptyStringTest = bytes(source);
        if (tempEmptyStringTest.length == 0) {
            return 0x0;
        }
        assembly {
            result := mload(add(source, 32))
        }
    }

    mapping(bytes32 => Person) public user;
    mapping(address => string) public UserMapping;
    mapping(bytes32 => address) public EmailMapping;
    string[] UserList;
    
    mapping(address => Claim[]) public UserClaim;
    
    mapping(address => mapping (address => string)) allowed;

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
        EmailMapping[stringToBytes32(email)] = publickey;
        UserList.push(email);
    }

    function GetUserInfo(bytes32 account) public returns (string) {
	return user[account].ObjectKey;
    }

    function SetUserInfo(bytes32 account, string new_objectkey){
        user[account].ObjectKey = new_objectkey;
    }

    function GetUserMapping(address publickey) public returns (string){
        return UserMapping[publickey];
    }

    function GetEmailMapping(string email) public returns (address){
        return EmailMapping[stringToBytes32(email)];
    }

    function MakeClaim(address subject, string key, string value){
        Claim newClaim;
        newClaim.Issuer = msg.sender;
        newClaim.Subject = subject;
        newClaim.Key = key;
        newClaim.Value = value;
        UserClaim[msg.sender].push(newClaim);
    }

    function GetUserClaim(address issuer, uint index)public returns (address,address,string,string){
        return (UserClaim[issuer][index].Issuer,UserClaim[issuer][index].Subject,UserClaim[issuer][index].Key,UserClaim[issuer][index].Value);
    }

    function approve(address spender, string _data){
        allowed[msg.sender][spender] = _data;
    }
    
    function GetUserAllowance(address Owner) public constant returns (string){
        return allowed[Owner][msg.sender];
    }

}
