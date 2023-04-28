from brownie import network, accounts, interface, config, web3
from .helpers import get_account, deploy_with_gas, DEPOSIT_AMOUNT, call_contract_method
from copy import copy


def main():
    account = get_account()
    pool = get_pool()
    # breakpoint()
    erc20_token = config['networks'][network.show_active()]['weth_token']
    if network.show_active() == "mainnet-fork":
        get_weth()

    approve_tx = approve_erc20(
        DEPOSIT_AMOUNT, pool.address, erc20_token, account)

    print('start deposit...')
    depost_tx = pool.supply(erc20_token, DEPOSIT_AMOUNT,
                            account, 0, {'from': account})
    depost_tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt_eth, available_borrow_token = get_borrowable_data(
        pool, account)

    print("Let's borrow!")

    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth -> borrowable_dai * 95%\
    borrow(pool, amount_dai_to_borrow, account)
    # repay borrowed money
    repay_all(amount_dai_to_borrow, pool, account)


def get_pool():
    account = get_account()
    address_provider = interface.IPoolAddressesProvider(
        config['networks'][network.show_active()]['lending_pool_addresses_provider'])
    pool_address = address_provider.getPool()
    return interface.IPool(pool_address)


def get_weth():
    weth = interface.IWeth(
        config['networks'][network.show_active()]['weth_token'])
    tx = weth.deposit({'from': get_account(), 'value': DEPOSIT_AMOUNT})
    tx.wait(1)
    print(f"Received {DEPOSIT_AMOUNT} WETH.")


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = call_contract_method(
        erc20, 'approve', spender, amount, {'from': account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_borrowable_data(pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = pool.getUserAccountData(account.address)
    available_borrow_token = copy(available_borrow_eth)
    oracle = get_price_oracle()
    asset_price = oracle.getAssetPrice(
        config["networks"][network.show_active()]["weth_token"])
    available_borrow_eth = available_borrow_eth/asset_price
    total_collateral_eth = total_collateral_eth/asset_price
    total_debt_eth = total_debt_eth/asset_price
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth), float(available_borrow_token))


def get_price_oracle():
    address_provider = interface.IPoolAddressesProvider(
        config['networks'][network.show_active()]['lending_pool_addresses_provider'])
    return interface.IPriceOracle(address_provider.getPriceOracle())


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)


def borrow(pool, amount, account):
    print(f"We are going to borrow {amount} DAI")
    # Now we will borrow!
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = pool.borrow(dai_address, web3.toWei(amount, "ether"),
                            2, 0, account.address, {'from': account})
    borrow_tx.wait(1)

    print('Borrowed!')

    borrowable_eth, total_debt_eth, available_borrow_token = get_borrowable_data(
        pool, account)


def repay_all(amount, pool, account):
    print(f"We are going to repay {amount} DAI")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(web3.toWei(amount, "ether"),
                  pool.address, dai_address, account)
    reapay_tx = pool.repay(dai_address, web3.toWei(
        amount, "ether"), 2, account.address, {'from': account})
    reapay_tx.wait(1)
    print("repay process ended successfully.")
    borrowable_eth, total_debt_eth, available_borrow_token = get_borrowable_data(
        pool, account)
