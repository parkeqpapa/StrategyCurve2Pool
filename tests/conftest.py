import pytest
from brownie import config
from brownie import Contract


@pytest.fixture
def gov(accounts):
    yield accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)


@pytest.fixture
def user(accounts):
    yield accounts[0]


@pytest.fixture
def rewards(accounts):
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    yield accounts[2]


@pytest.fixture
def management(accounts):
    yield accounts[3]


@pytest.fixture
def strategist(accounts):
    yield accounts[4]


@pytest.fixture
def keeper(accounts):
    yield accounts[5]


@pytest.fixture
def token():
    token_address = "0x27E611FD27b276ACbd5Ffd632E5eAEBEC9761E40"  # this should be the address of the ERC-20 used by the strategy/vault (DAI)
    yield Contract(token_address)


@pytest.fixture
def amount(accounts, token, user):
    amount = 10_000 * 10 ** token.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.
    reserve = accounts.at("0x8866414733F22295b7563f9C5299715D2D76CAf4", force=True)
    token.transfer(user, amount, {"from": reserve})
    yield amount


@pytest.fixture
def weth():
    token_address = "0x74b23882a30290451A17c44f4F05243b6b58C76d"
    yield Contract(token_address)


@pytest.fixture
def weth_amount(user, weth):
    weth_amount = 10 ** weth.decimals()
    weth.transfer(user, weth_amount, {"from": weth})
    yield weth_amount


@pytest.fixture
def vault(pm, gov, rewards, guardian, management, token):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian, management)
    vault.setDepositLimit(2**256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture
def strategy(strategist, keeper, vault, Strategy, gov):
    strategy = strategist.deploy(Strategy, vault)
    strategy.setKeeper(keeper)
    vault.addStrategy(strategy, 10_000, 0, 2**256 - 1, 1_000, {"from": gov})
    yield strategy


@pytest.fixture(scope="session")
def RELATIVE_APPROX():
    yield 1e-5


# Function scoped isolation fixture to enable xdist.
# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass