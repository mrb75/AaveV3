# Introduction
in this project some of the base application of Aave protocol are deployed by [eth-brownie](https://eth-brownie.readthedocs.io/) framework.



# How to use
- clone this repository in your system 
- create virtual enviroment
create a virtual enviroment in your python by using [python venv documentation](https://docs.python.org/3/library/venv.html).

- activate you enviroment
based on [python venv documentation](https://docs.python.org/3/library/venv.html)

- install brownie on venv

```console
pip install eth-brownie
```

- create .env file and copy:
```.env
WEB3_ALCHEMY_PROJECT_ID = "your WEB3_ALCHEMY_PROJECT_ID"
ETHERSCAN_TOKEN = "your ETHERSCAN_TOKEN"

```

- compile interfaces
```console
brownie comile
```

- run scripts

```console
brownie run scripts/deployment_v3.py --network=mainnet-fork
```
**Note**
    you can use "mainnet" or "testnets" also


