const ERTBRM = artifacts.require("ERTBRM");

contract("ERTBRM", (accounts) => {
    let instance;
    const gasPrice = web3.utils.toWei("20", "gwei"); // 统一的 Gas Price

    before(async () => {
        // 使用 new() 创建一个全新的合约实例
        instance = await ERTBRM.new();
        assert(instance.address, "Contract is not deployed"); // 确保合约已部署
    });

    it("should upload data and log gas cost", async () => {
        const tx = await instance.uploadData(1, "Test Metadata", { from: accounts[0] });
        const gasUsed = tx.receipt.gasUsed;
        const gasCost = gasUsed * gasPrice;

        console.log("Gas used for uploadData:", gasUsed);
        console.log("Gas cost in Ether:", web3.utils.fromWei(gasCost.toString(), "ether"), "ETH");

        // 验证事件
        assert.equal(tx.logs[0].event, "DataUploaded", "DataUploaded event not emitted");

        // 验证数据存储
        const data = await instance.dataRegistry(1);
        assert.equal(data.metadata, "Test Metadata", "Data metadata is incorrect");
    });

    it("should grant access and log gas cost", async () => {
        const tx = await instance.grantAccess(accounts[1], { from: accounts[0] });
        const gasUsed = tx.receipt.gasUsed;
        const gasCost = gasUsed * gasPrice;

        console.log("Gas used for grantAccess:", gasUsed);
        console.log("Gas cost in Ether:", web3.utils.fromWei(gasCost.toString(), "ether"), "ETH");

        // 验证事件
        assert.equal(tx.logs[0].event, "AccessGranted", "AccessGranted event not emitted");

        // 验证访问权限
        const hasAccess = await instance.accessControl(accounts[1]);
        assert.equal(hasAccess, true, "Access not granted correctly");
    });

    it("should revoke access and log gas cost", async () => {
        const tx = await instance.revokeAccess(accounts[1], { from: accounts[0] });
        const gasUsed = tx.receipt.gasUsed;
        const gasCost = gasUsed * gasPrice;

        console.log("Gas used for revokeAccess:", gasUsed);
        console.log("Gas cost in Ether:", web3.utils.fromWei(gasCost.toString(), "ether"), "ETH");

        // 验证事件
        assert.equal(tx.logs[0].event, "AccessRevoked", "AccessRevoked event not emitted");

        // 验证访问权限
        const hasAccess = await instance.accessControl(accounts[1]);
        assert.equal(hasAccess, false, "Access not revoked correctly");
    });

    it("should update reputation and log gas cost", async () => {
        const tx = await instance.updateReputation(accounts[2], 100, { from: accounts[0] });
        const gasUsed = tx.receipt.gasUsed;
        const gasCost = gasUsed * gasPrice;

        console.log("Gas used for updateReputation:", gasUsed);
        console.log("Gas cost in Ether:", web3.utils.fromWei(gasCost.toString(), "ether"), "ETH");

        // 验证事件
        assert.equal(tx.logs[0].event, "ReputationUpdated", "ReputationUpdated event not emitted");

        // 验证信誉分数
        const reputation = await instance.reputation(accounts[2]);
        assert.equal(reputation.toNumber(), 100, "Reputation not updated correctly");
    });

    it("should initiate arbitration and log gas cost", async () => {
        const tx = await instance.initiateArbitration("Dispute description", { from: accounts[0] });
        const gasUsed = tx.receipt.gasUsed;
        const gasCost = gasUsed * gasPrice;

        console.log("Gas used for initiateArbitration:", gasUsed);
        console.log("Gas cost in Ether:", web3.utils.fromWei(gasCost.toString(), "ether"), "ETH");

        // 验证事件
        assert.equal(tx.logs[0].event, "ArbitrationInitiated", "ArbitrationInitiated event not emitted");

        // 验证仲裁数据
        const arbitration = await instance.arbitrations(1);
        assert.equal(arbitration.resolution, "Dispute description", "Arbitration resolution not stored correctly");
        assert.equal(arbitration.resolved, false, "Arbitration should not be resolved initially");
    });

    it("should resolve arbitration and log gas cost", async () => {
        const tx = await instance.resolveArbitration(1, "Dispute resolved", { from: accounts[0] });
        const gasUsed = tx.receipt.gasUsed;
        const gasCost = gasUsed * gasPrice;

        console.log("Gas used for resolveArbitration:", gasUsed);
        console.log("Gas cost in Ether:", web3.utils.fromWei(gasCost.toString(), "ether"), "ETH");

        // 验证事件
        assert.equal(tx.logs[0].event, "ArbitrationResolved", "ArbitrationResolved event not emitted");

        // 验证仲裁数据
        const arbitration = await instance.arbitrations(1);
        assert.equal(arbitration.resolved, true, "Arbitration not resolved");
        assert.equal(arbitration.resolution, "Dispute resolved", "Arbitration resolution not updated correctly");
    });
});
