from brownie import accounts, network, config
from functools import wraps
LOCAL_ENVIRONMENTS = ['development', 'ganache-local']
FORKED_LOCAL_ENVIROMENT = ['mainnet-fork', 'mainnet-fork-dev']
AGGREGATOR_DECIMAIL = 8
AGGREGATOR_INITIAL_ANSWER = 2e11
DEPOSIT_AMOUNT = "0.1 ether"


def get_account():
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        account = accounts[0]
    else:
        account = accounts.load("mymeta")
    return account


def get_price_feed_address():
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        if not (MockV3Aggregator):
            MockV3Aggregator.deploy(AGGREGATOR_DECIMAIL, AGGREGATOR_INITIAL_ANSWER, {
                                    'from': get_account(), 'gas_price': '60 gwei'})
        aggregator = MockV3Aggregator[-1]
        address = aggregator.address
    else:
        address = config['networks'][network.show_active()
                                     ]['eth_usd_price_feed']
    return address


def deploy_with_gas(contract, *args, **kwargs):
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        gas_price = "60 gwei"
        args[-1]['gas_price'] = gas_price
        args[-1]["gas_limit"] = 12000000
    contract.deploy(*args, **kwargs)


def only_local_env_test(func):
    from pytest import skip

    @wraps(func)
    def wrapper(*args, **kwargs):
        if network.show_active() not in LOCAL_ENVIRONMENTS:
            skip("only for local testing")
        result = func(*args, **kwargs)
        return result

    return wrapper


def call_contract_method(contract, method_name: str, *args, **kwargs):
    if network.show_active() in LOCAL_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIROMENT:
        args[-1]["gas_price"] = "60 gwei"
        args[-1]["gas_limit"] = 12000000
    # args[-1]["gas_limit"] = 120000000000
    return getattr(contract, method_name)(*args, **kwargs)


def calculate_tx_fee(tx_receipt):
    return tx_receipt.gas_used*tx_receipt.gas_price
