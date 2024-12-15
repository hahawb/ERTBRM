// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ABETokenAccessControl {
    struct User {
        uint reputationLevel;
        bool isRegistered;
    }

    struct Data {
        uint sensitivityLevel;
        string dataContent;
    }

    mapping(address => User) public users;
    mapping(uint => Data) public dataItems;
    mapping(address => bool) public tokenGranted;

    event AccessControlResult(address indexed user, uint indexed dataId, bool accessGranted);

    // 注册用户
    function registerUser(address _userAddress, uint _reputationLevel) public {
        require(!users[_userAddress].isRegistered, "User already registered.");
        users[_userAddress] = User(_reputationLevel, true);
    }

    // 添加数据
    function addData(uint _dataId, uint _sensitivityLevel, string memory _dataContent) public {
        dataItems[_dataId] = Data(_sensitivityLevel, _dataContent);
    }

    // 发放令牌
    function grantToken(address _userAddress) public {
        require(users[_userAddress].isRegistered, "User not registered.");
        tokenGranted[_userAddress] = true;
    }

    // 请求数据访问
    function requestDataAccess(uint _dataId) public {
        require(users[msg.sender].isRegistered, "User not registered.");
        require(tokenGranted[msg.sender], "Token not granted.");
        User memory user = users[msg.sender];
        Data memory data = dataItems[_dataId];

        bool accessGranted;
        if ((user.reputationLevel >= 3 && data.sensitivityLevel <= 3) || 
            (user.reputationLevel == 2 && data.sensitivityLevel <= 2) ||
            (user.reputationLevel == 1 && data.sensitivityLevel == 1)) {
            accessGranted = true;
        } else {
            accessGranted = false;
        }

        emit AccessControlResult(msg.sender, _dataId, accessGranted);
    }
}
