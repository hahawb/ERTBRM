const ABETokenAccessControl = artifacts.require("ABETokenAccessControl");

contract("ABETokenAccessControl", accounts => {
    let atc;
    const gasPrice = web3.utils.toWei("20", "gwei"); // 统一的 Gas Price

    before(async () => {
        atc = await ABETokenAccessControl.new();
    });

    it("should register, grant token, add data, and request access", async () => {
        const user = accounts[1];
        const dataId = 1;

        // 注册用户并添加数据
        await atc.registerUser(user, 3);
        await atc.grantToken(user);
        await atc.addData(dataId, 3, "High sensitivity data");

        // 请求访问并记录 Gas 消耗
        const receipt = await atc.requestDataAccess(dataId, { from: user, gasPrice: gasPrice });
        const gasUsed = receipt.receipt.gasUsed;
        const gasCost = gasUsed * gasPrice;

        console.log(`Gas used for ABETokenAccessControl (request access): ${gasUsed}`);
        console.log(`Gas cost in Ether: ${web3.utils.fromWei(gasCost.toString(), "ether")} ETH`);
    });
});
