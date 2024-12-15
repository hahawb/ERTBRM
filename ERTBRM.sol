// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

contract ERTBRM {
    struct CTIData {
        uint256 id;
        string metadata;
        address uploader;
    }

    struct Arbitration {
        uint256 disputeId;
        address initiator;
        string resolution;
        bool resolved;
    }

    mapping(uint256 => CTIData) public dataRegistry;
    mapping(address => uint256) public reputation;
    mapping(uint256 => Arbitration) public arbitrations;
    mapping(address => bool) public accessControl;

    event DataUploaded(uint256 id, string metadata, address uploader);
    event AccessGranted(address user);
    event AccessRevoked(address user);
    event ReputationUpdated(address user, uint256 newScore);
    event ArbitrationInitiated(uint256 disputeId, address initiator);
    event ArbitrationResolved(uint256 disputeId, string resolution);

    uint256 public arbitrationCount;

    // 上传数据
    function uploadData(uint256 id, string memory metadata) public {
        require(bytes(metadata).length > 0, "Metadata cannot be empty");
        dataRegistry[id] = CTIData(id, metadata, msg.sender);
        emit DataUploaded(id, metadata, msg.sender);
    }

    // 请求数据
    function requestData(uint256 id) public view returns (string memory) {
        require(accessControl[msg.sender], "Access denied");
        require(dataRegistry[id].id == id, "Data not found");
        return dataRegistry[id].metadata;
    }

    // 授权访问
    function grantAccess(address user) public {
        accessControl[user] = true;
        emit AccessGranted(user);
    }

    // 撤销访问
    function revokeAccess(address user) public {
        accessControl[user] = false;
        emit AccessRevoked(user);
    }

    // 更新信誉分数
    function updateReputation(address user, uint256 newScore) public {
        require(user != address(0), "Invalid address");
        reputation[user] = newScore;
        emit ReputationUpdated(user, newScore);
    }

    // 启动仲裁
    function initiateArbitration(string memory disputeDescription) public {
        arbitrationCount++;
        arbitrations[arbitrationCount] = Arbitration({
            disputeId: arbitrationCount,
            initiator: msg.sender,
            resolution: disputeDescription,
            resolved: false
        });
        emit ArbitrationInitiated(arbitrationCount, msg.sender);
    }

    // 解决仲裁
    function resolveArbitration(uint256 disputeId, string memory resolution) public {
        Arbitration storage arbitration = arbitrations[disputeId];
        require(!arbitration.resolved, "Arbitration already resolved");
        arbitration.resolution = resolution;
        arbitration.resolved = true;
        emit ArbitrationResolved(disputeId, resolution);
    }
}
