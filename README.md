# SUI-QUEST

this script playing human for points in [quests](https://quests.mystenlabs.com/).<br>
[donations are welcome](https://cyberomanov.tech/WTF_donate), if you find this tool helpful.

## Contents
1. [Installation](https://github.com/cyberomanov/sui-bullshark#installation)

## Installation
1. make sure you have installed `python3.10` or newer;
2. setup your `config.py`, `data/mnemonic.txt`, `data/transfer.txt`;
3. install requirements `pip3 install -r requirements.txt`;
4. run the script `python3 quest.py`.
```bash
1. navi_deposit_borrow_repay();             # there is no withdraw module!
2. scallop_deposit_liquidity();             # following the config
3. scallop_withdraw_liquidity();            # 100% of provided liquidity
4. kriya_swap(from_token=SUI);              # to $USDC only, following the config
5. kriya_swap(from_token=USDC);             # to $SUI only, 100% of balance

55. report();
56. transfer();
57. mnemonic_generator();
```
## Update
1. `cd sui-bullshark`
2. `git fetch && git reset --hard && git pull`
3. `pip3 install -r requirements.txt`
4. `python3 quest.py`.